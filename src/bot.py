#
# Copyright (c) 2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from transcript_handler import TranscriptHandler
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.processors.transcript_processor import TranscriptProcessor
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecatcloud.agent import DailySessionArguments
from pydantic import BaseModel
from typing import Optional

from config import (
    ENV_VARS,
    TTS_CONFIG,
    LLM_CONFIG,
    BOT_NAMES,
    EVENT_HANDLERS,
    LOG_MESSAGES,
    SYSTEM_MESSAGES,
)

# Load environment variables
load_dotenv(override=True)

# Check if we're in local development mode
LOCAL_RUN = os.getenv(ENV_VARS["LOCAL_RUN"])
if LOCAL_RUN:
    import argparse
    import asyncio
    import webbrowser

    try:
        # Required to run local_runner.py
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from local_runner import configure
    except ImportError:
        logger.error(LOG_MESSAGES["import_error"])

class BodyRequest(BaseModel):
    user_context: Optional[str] = None

class RecordingState:
    def __init__(self):
        self.isRecording = False
    
    def start_recording(self):
        self.isRecording = True
    
    def stop_recording(self):
        self.isRecording = False


async def main(transport: DailyTransport, user_context: Optional[str] = None):
    """Main pipeline setup and execution function.

    Args:
        transport: The DailyTransport instance
    """
    tts = CartesiaTTSService(
        api_key=os.getenv(ENV_VARS["CARTESIA_API_KEY"]), voice_id=TTS_CONFIG["voice_id"]
    )

    sst = DeepgramSTTService(
        api_key=os.getenv(ENV_VARS["DEEPGRAM_API_KEY"]),
    )

    llm = OpenAILLMService(api_key=os.getenv(ENV_VARS["OPENAI_API_KEY"]), model=LLM_CONFIG["model"])

    content = SYSTEM_MESSAGES["initial_system_prompt"]
    if user_context:
        content += f"\n\nUser context: {user_context}"

    messages = [
        {
            "role": "system",
            "content": content,
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Transcript Processor
    transcript = TranscriptProcessor()

    # Transcript Handler
    transcript_handler = TranscriptHandler()

    pipeline = Pipeline(
        [
            transport.input(),
            sst,
            transcript.user(),
            context_aggregator.user(),
            llm,
            tts,
            transport.output(),
            transcript.assistant(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
            report_only_initial_ttfb=True,
        ),
    )

    recording_state = RecordingState()



    @transport.event_handler(EVENT_HANDLERS["on_client_connected"])
    async def on_client_connected(transport: DailyTransport, client):
        logger.info(LOG_MESSAGES["on_client_connected"], client["id"])
        await transport.start_recording()
        recording_state.start_recording()
        # Kick off the conversation.
       # messages.append(
       #     {
       #         "role": "system",
       #         "content": SYSTEM_MESSAGES["start_conversation"],
       #     }
       # )
       # await task.queue_frames([LLMMessagesFrame(messages)])
        # Empty frame to start the conversation
        await task.queue_frames([context_aggregator.user().get_context_frame()])

    @transport.event_handler(EVENT_HANDLERS["on_client_disconnected"])
    async def on_client_disconnected(transport: DailyTransport, client):
        logger.info(LOG_MESSAGES["on_client_disconnected"], client)
        if recording_state.isRecording:
            await transport.stop_recording()
            recording_state.stop_recording()
        await task.cancel()

    @transport.event_handler(EVENT_HANDLERS["on_recording_started"])
    async def on_recording_started(transport, status):
        logger.info(LOG_MESSAGES["recording_started"], status)
    
    # https://reference-python.daily.co/api_reference.html#daily.EventHandler.on_recording_error
    @transport.event_handler(EVENT_HANDLERS["on_recording_error"])
    async def on_recording_error(transport, stream_id, message):
        logger.error(LOG_MESSAGES["recording_error"], message)

    @transport.event_handler(EVENT_HANDLERS["on_recording_stopped"])
    async def on_recording_stopped(transport, status):
        logger.info(LOG_MESSAGES["recording_stopped"], status)
    
    # Register event handler for transcript updates
    @transcript.event_handler("on_transcript_update")
    async def on_transcript_update(processor, frame):
        await transcript_handler.on_transcript_update(processor, frame)

    runner = PipelineRunner()

    await runner.run(task)


async def bot(args: DailySessionArguments):
    """Main bot entry point compatible with the FastAPI route handler.

    Args:
        room_url: The Daily room URL
        token: The Daily room token
        body: The configuration object from the request body
        session_id: The session ID for logging
    """
    logger.info(LOG_MESSAGES["bot_initialized"], args.room_url, args.token)

    body = args.body
    validated_body = BodyRequest.model_validate(body or {})
    user_context = validated_body.user_context

    transport = DailyTransport(
        args.room_url,
        args.token,
        BOT_NAMES["production"],
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            transcription_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    try:
        await main(transport, user_context)
        logger.info(LOG_MESSAGES["bot_completed"])
    except Exception as e:
        logger.exception(LOG_MESSAGES["bot_error"], str(e))
        raise


# Local development
async def local_daily(data: Optional[str] = None):
    """Daily transport for local development.
    
    Args:
        data: Optional data parameter to pass as user context
    """

    try:
        # Validate data using BodyRequest
        validated_body = BodyRequest.model_validate({"user_context": data} if data else {})
        user_context = validated_body.user_context

        async with aiohttp.ClientSession() as session:
            (room_url, token) = await configure(session)
            transport = DailyTransport(
                room_url,
                token,
                BOT_NAMES["local"],
                params=DailyParams(
                    audio_in_enabled=True,
                    audio_out_enabled=True,
                    transcription_enabled=True,
                    vad_analyzer=SileroVADAnalyzer(),
                ),
            )

            logger.warning(LOG_MESSAGES["local_agent_url"], room_url)
            webbrowser.open(room_url)

            await main(transport, user_context)
    except Exception as e:
        logger.exception(LOG_MESSAGES["local_dev_error"], e)


# Local development entry point
if LOCAL_RUN and __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Local development for Pipecat agent")
        parser.add_argument("--data", type=str, help="Data to pass as user context")
        args = parser.parse_args()
        
        asyncio.run(local_daily(args.data))
    except Exception as e:
        logger.exception(LOG_MESSAGES["local_run_failed"], e)

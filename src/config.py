"""
Configuration file containing all strings and constants used in the bot application.
"""

# Environment variable names
ENV_VARS = {
    "LOCAL_RUN": "LOCAL_RUN",
    "CARTESIA_API_KEY": "CARTESIA_API_KEY",
    "DEEPGRAM_API_KEY": "DEEPGRAM_API_KEY",
    "OPENAI_API_KEY": "OPENAI_API_KEY",
}

# TTS Configuration
TTS_CONFIG = {
    # My voice clone
    # "voice_id": "efe5d4cb-be7a-4aa6-9294-5ea6b762f837",
    "voice_id": "78ab82d5-25be-4f7d-82b3-7ad64e5b85b2",
}

# LLM Configuration
LLM_CONFIG = {
    "model": "gpt-4o",
}

# Bot Names
BOT_NAMES = {
    "production": "Hello Bot",
    "local": "Hello Bot",
}

# Event Handler Names
EVENT_HANDLERS = {
    "on_first_participant_joined": "on_first_participant_joined",
    "on_client_connected": "on_client_connected",
    "on_client_disconnected": "on_client_disconnected",
    "on_recording_started": "on_recording_started",
    "on_recording_error": "on_recording_error",
    "on_recording_stopped": "on_recording_stopped",
}

# Log Messages
LOG_MESSAGES = {
    "import_error": "Could not import local_runner module. Local development mode may not work.",
    "on_client_connected": "First participant joined: {}",
    "on_client_disconnected": "Participant left: {}",
    "bot_initialized": "Bot process initialized {} {}",
    "bot_completed": "Bot process completed",
    "bot_error": "Error in bot process: {}",
    "local_agent_url": "Talk to your voice agent here: {}",
    "local_dev_error": "Error in local development mode: {}",
    "local_run_failed": "Failed to run in local mode: {}",
    "recording_started": "Recording started: {}",
    "recording_error": "Recording error: {}",
    "recording_stopped": "Recording stopped: {}",
}

# System Messages
SYSTEM_MESSAGES = {
    "initial_system_prompt": """You are a helpful assistant who is good at dad jokes. End conversation when the user says goodbye.""",
    "start_conversation": "Introduce yourself to the user. If user's context is provided, use it to introduce yourself.",
}

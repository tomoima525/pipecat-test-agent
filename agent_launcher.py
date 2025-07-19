## Launch Agent deployed on Pipecat Cloud

import asyncio
import argparse
import json
import os
from dotenv import load_dotenv
from pipecatcloud import AgentStartError
from pipecatcloud.session import Session, SessionParams

load_dotenv()

async def launch_agent(agent_name: str="recruiter", data: dict = None):
    """
       Create a room using Agent Session fromp Pipecat Cloud
    """
    key = os.getenv("PIPECAT_CLOUD_API_KEY")
    print("key", key)
    bucket_name = os.getenv("BUCKET_NAME")
    bucket_region = os.getenv("BUCKET_REGION")
    assume_role_arn = os.getenv("ASSUME_ROLE_ARN")

    if not bucket_name:
        raise Exception("BUCKET_NAME environment variable is required when RECORD_VIDEO is enabled")
    if not bucket_region:
        raise Exception("BUCKET_REGION environment variable is required when RECORD_VIDEO is enabled")
    if not assume_role_arn:
        raise Exception("ASSUME_ROLE_ARN environment variable is required when RECORD_VIDEO is enabled")

    transcription_bucket_name = bucket_name
    transcription_bucket_region = bucket_region
    transcription_assume_role_arn = assume_role_arn

    transcription_bucket = {
        "bucket_name": transcription_bucket_name,
        "bucket_region": transcription_bucket_region,
        "assume_role_arn": transcription_assume_role_arn,
        "allow_api_access": True
    }
        
    properties = {
        "enable_prejoin_ui": False, 
        "enable_recording": "cloud", 
        "recordings_bucket": {
            "bucket_name": bucket_name,
            "bucket_region": bucket_region,
            "assume_role_arn": assume_role_arn,
            "allow_api_access": True
        },
        "transcription_bucket": transcription_bucket
    }
    try:
        session = Session(
            api_key=key,
            agent_name=agent_name,
            params=SessionParams(
                use_daily=True,
                data=data,
                daily_room_properties=properties
            )
        )
        print("session", session)
        response = await session.start()
        print(f"Daily URL: {response['dailyRoom']}?t={response['dailyToken']}")
        daily_url = f"{response['dailyRoom']}?t={response['dailyToken']}"
        return daily_url
    except AgentStartError as e:
        print(f"Error starting agent: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Launch Agent deployed on Pipecat Cloud')
    parser.add_argument('--agent-name', default='pipecat-test-agent', help='Name of the agent to launch')
    parser.add_argument('--data', type=str, help='JSON data to pass to the agent')
    
    args = parser.parse_args()
    
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON data: {e}")
            return
    
    asyncio.run(launch_agent(agent_name=args.agent_name, data=data))

if __name__ == "__main__":
    main()
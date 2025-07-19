#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

import os
from dotenv import load_dotenv

import aiohttp
from fastapi import HTTPException
from pipecat.transports.services.helpers.daily_rest import DailyRESTHelper, DailyRoomParams

# Load environment variables from .env file
load_dotenv()


async def configure(aiohttp_session: aiohttp.ClientSession):
    # (url, token) = await configure_with_args(aiohttp_session)
    (url, token) = await configure_with_args(aiohttp_session)
    return (url, token)

RECORD_VIDEO = os.getenv("RECORD_VIDEO")

print("RECORD_VIDEO", RECORD_VIDEO)


async def configure_with_args(aiohttp_session: aiohttp.ClientSession = None):
    key = os.getenv("DAILY_API_KEY")
    if not key:
        raise Exception(
            "No Daily API key specified. set DAILY_API_KEY in your environment to specify a Daily API key, available from https://dashboard.daily.co/developers."
        )

    daily_rest_helper = DailyRESTHelper(
        daily_api_key=key,
        daily_api_url=os.getenv("DAILY_API_URL", "https://api.daily.co/v1"),
        aiohttp_session=aiohttp_session,
    )
    # Get S3 bucket configuration from environment variables
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

    if RECORD_VIDEO == True:
        
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
    else:
        properties = {"enable_prejoin_ui": False, "transcription_bucket": transcription_bucket}

    room = await daily_rest_helper.create_room(
        DailyRoomParams(properties=properties)
    )
    if not room.url:
        raise HTTPException(status_code=500, detail="Failed to create room")

    url = room.url

    # Create a meeting token for the given room with an expiration 1 hour in
    # the future.
    expiry_time: float = 60 * 60

    token = await daily_rest_helper.get_token(url, expiry_time)

    return (url, token)

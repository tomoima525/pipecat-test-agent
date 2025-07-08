# CLAUDE.md

This file provides context for Claude about the Pipecat Cloud Voice Agent Starter project.

## Project Overview

This is a **Pipecat Cloud Voice Agent Starter Template** - a conversational AI application built on the Pipecat framework for creating voice-enabled AI agents. The project demonstrates how to build and deploy a voice agent to Daily's Pipecat Cloud platform using WebRTC for real-time voice communication.

## Project Structure

```
/
├── src/
│   ├── bot.py              # Main application entry point
│   └── config.py           # Centralized configuration management
├── local_runner.py         # Local development utilities
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── pcc-deploy.toml        # Deployment configuration
├── README.md              # Project documentation
└── env.example            # Environment variable template
```

## Key Components

### Core Application (`src/bot.py`)
- **Main entry point** for the voice agent
- Implements WebRTC-based voice conversation using DailyTransport
- Includes recording functionality with state management
- Handles participant events (join/leave)
- Configured as a "helpful assistant who can answer questions about WebRTC"

### Configuration (`src/config.py`)
- **Centralized configuration management** with organized sections:
  - Environment variables
  - TTS settings (Cartesia)
  - LLM configuration (OpenAI GPT-4o)
  - Event handlers
  - Log messages
  - System prompts

### Local Development (`local_runner.py`)
- Creates Daily rooms for local testing
- Handles video recording configuration
- Manages authentication and room setup

## Dependencies

**Core Stack:**
- `pipecatcloud` - Pipecat Cloud SDK
- `pipecat-ai[cartesia,daily,openai,silero]` - Framework with integrations
- `python-dotenv` - Environment variable management

**Services:**
- **Cartesia** - Text-to-Speech (voice ID: `efe5d4cb-be7a-4aa6-9294-5ea6b762f837`)
- **OpenAI** - Language Model (GPT-4o)
- **Daily** - WebRTC transport
- **Silero** - Voice Activity Detection

## Environment Variables

**Required API Keys:**
- `CARTESIA_API_KEY` - Cartesia TTS service
- `OPENAI_API_KEY` - OpenAI LLM service
- `DAILY_API_KEY` - Daily WebRTC service (auto-provided in cloud)

**Development Variables:**
- `LOCAL_RUN=1` - Enable local development mode
- `RECORD_VIDEO=1` - Enable video recording in local mode
- `DAILY_API_URL` - Daily API endpoint (defaults to https://api.daily.co/v1)

## Development Commands

### Local Development
```bash
# Basic local run
LOCAL_RUN=1 python bot.py

# Local run with video recording
LOCAL_RUN=1 RECORD_VIDEO=1 python bot.py
```

### Build and Deploy
```bash
# Build ARM64 Docker image
docker build --platform=linux/arm64 -t pipecat-test-agent:latest .

# Deploy to Pipecat Cloud
pcc deploy pipecat-test-agent username/pipecat-test-agent:0.1 --secrets pipecat-test-agent-secrets

# Using config file
pcc deploy

# Start agent session
pcc agent start pipecat-test-agent --use-daily
```

## Current Configuration

- **Agent Name:** `pipecat-test-agent`
- **Docker Image:** `tomoima525/pipecat-test-agent:0.4`
- **Secret Set:** `pipecat-test-secrets`
- **Deployment:** Configured for scale-to-zero with 5-minute idle timeout

## Features

- **Real-time voice conversation** via WebRTC
- **Automatic recording** when participants join
- **Interruption handling** for natural conversation flow
- **Metrics and usage tracking**
- **Error logging and monitoring**
- **Graceful participant departure handling**

## Testing

**No formal testing framework currently implemented.** Consider adding:
- Unit tests for core functionality
- Integration tests for pipeline components
- Test configuration and CI/CD setup

## Common Issues and Solutions

1. **Local development import errors**: Ensure `local_runner.py` is in the correct path
2. **API key configuration**: Use `.env` file or environment variables
3. **Recording functionality**: Requires proper Daily API key configuration
4. **Docker build issues**: Ensure ARM64 platform for cloud deployment

## Development Tips

- Use `uv` for fast Python package management
- Check logs for debugging recording and participant events
- Test locally before deploying to cloud
- Monitor deployment status with `pcc agent status`
- Use Daily room URLs for testing voice interactions

## Recent Changes

- Moved core files to `src/` directory for better organization
- Added recording state management and event handlers
- Updated README examples to use consistent naming
- Enhanced local development debugging capabilities
- Updated deployment configuration to version 0.4
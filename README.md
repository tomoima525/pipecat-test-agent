# Pipecat

[![Docs](https://img.shields.io/badge/Documentation-blue)](https://docs.pipecat.daily.co) [![Discord](https://img.shields.io/discord/1217145424381743145)](https://discord.gg/dailyco)

A template voice agent for [Pipecat Cloud](https://www.daily.co/products/pipecat-cloud/) that demonstrates building and deploying a conversational AI agent.

> **For a detailed step-by-step guide, see our [Quickstart Documentation](https://docs.pipecat.daily.co/quickstart).**

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Linux, MacOS, or Windows Subsystem for Linux (WSL)
- [Docker](https://www.docker.com) and a Docker repository (e.g., [Docker Hub](https://hub.docker.com))
- A Docker Hub account (or other container registry account)
- [Pipecat Cloud](https://pipecat.daily.co) account

> **Note**: If you haven't installed Docker yet, follow the official installation guides for your platform ([Linux](https://docs.docker.com/engine/install/), [Mac](https://docs.docker.com/desktop/setup/install/mac-install/), [Windows](https://docs.docker.com/desktop/setup/install/windows-install/)). For Docker Hub, [create a free account](https://hub.docker.com/signup) and log in via terminal with `docker login`.

## Get Started

### 1. Get the starter project

Clone the starter project from GitHub:

```bash
git clone https://github.com/daily-co/pipecat-cloud-starter
cd pipecat-cloud-starter
```

### 2. Set up your Python environment

We recommend using a virtual environment to manage your Python dependencies.

```bash
# Create a virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the Pipecat Cloud CLI
uv pip install pipecatcloud
```

### 3. Authenticate with Pipecat Cloud

```bash
pcc auth login
```

### 4. Acquire required API keys

This starter requires the following API keys:

- **OpenAI API Key**: Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Cartesia API Key**: Get from [play.cartesia.ai/keys](https://play.cartesia.ai/keys)
- **Daily API Key**: Automatically provided through your Pipecat Cloud account

### 5. Configure to run locally (optional)

You can test your agent locally before deploying to Pipecat Cloud:

```bash
# Set environment variables with your API keys
export CARTESIA_API_KEY="your_cartesia_key"
export DAILY_API_KEY="your_daily_key"
export OPENAI_API_KEY="your_openai_key"
```

> Your `DAILY_API_KEY` can be found at [https://pipecat.daily.co](https://pipecat.daily.co) under the `Settings` in the `Daily (WebRTC)` tab.

First install requirements:

```bash
uv pip install -r requirements.txt
```

Then, launch the bot.py script locally:

```bash
LOCAL_RUN=1 python src/bot.py
```

or record video locally (requires S3 configuration):

```bash
# Set required S3 environment variables in .env file:
# BUCKET_NAME=your-bucket-name
# BUCKET_REGION=us-west-2
# ASSUME_ROLE_ARN=arn:aws:iam::123456789012:role/your-role

LOCAL_RUN=1 RECORD_VIDEO=1 python bot.py
```

## Deploy & Run

### 1. Build and push your Docker image

```bash
# Build the image (targeting ARM architecture for cloud deployment)
docker build --platform=linux/arm64 -t pipecat-test-agent:latest .

# Tag with your Docker username and version
docker tag pipecat-test-agent:latest your-username/pipecat-test-agent:0.1

# Push to Docker Hub
docker push your-username/pipecat-test-agent:0.1
```

### 2. Create a secret set for your API keys

The starter project requires API keys for OpenAI and Cartesia:

```bash
# Copy the example env file
cp env.example .env

# Edit .env to add your API keys:
# CARTESIA_API_KEY=your_cartesia_key
# OPENAI_API_KEY=your_openai_key

# For video recording, also add S3 configuration:
# BUCKET_NAME=your-bucket-name
# BUCKET_REGION=us-west-2
# ASSUME_ROLE_ARN=arn:aws:iam::123456789012:role/your-role

# Create a secret set from your .env file
pcc secrets set pipecat-test-agent-secrets --file .env
```

Alternatively, you can create secrets directly via CLI:

```bash
pcc secrets set pipecat-test-agent-secrets \
  CARTESIA_API_KEY=your_cartesia_key \
  OPENAI_API_KEY=your_openai_key
```

### 3. Deploy to Pipecat Cloud

```bash
pcc deploy pipecat-test-agent your-username/pipecat-test-agent:0.1 --secrets pipecat-test-agent-secrets
```

> **Note (Optional)**: For a more maintainable approach, you can use the included `pcc-deploy.toml` file:
>
> ```toml
> agent_name = "pipecat-test-agent"
> image = "your-username/pipecat-test-agent:0.1"
> secret_set = "pipecat-test-agent-secrets"
>
> [scaling]
>     min_instances = 0
> ```
>
> Then simply run `pcc deploy` without additional arguments.

> **Note**: If your repository is private, you'll need to add credentials:
>
> ```bash
> # Create pull secret (you’ll be prompted for credentials)
> pcc secrets image-pull-secret pull-secret https://index.docker.io/v1/
>
> # Deploy with credentials
> pcc deploy pipecat-test-agent your-username/pipecat-test-agent:0.1 --credentials pull-secret
> ```

### 4. Check deployment and scaling (optional)

By default, your agent will use "scale-to-zero" configuration, which means it may have a cold start of around 10 seconds when first used. By default, idle instances are maintained for 5 minutes before being terminated when using scale-to-zero.

For more responsive testing, you can scale your deployment to keep a minimum of one instance warm:

```bash
# Ensure at least one warm instance is always available
pcc deploy pipecat-test-agent your-username/pipecat-test-agent:0.1 --min-instances 1

# Check the status of your deployment
pcc agent status pipecat-test-agent
```

By default, idle instances are maintained for 5 minutes before being terminated when using scale-to-zero.

### 5. Create an API key

```bash
# Create a public API key for accessing your agent
pcc organizations keys create

# Set it as the default key to use with your agent
pcc organizations keys use
```

### 6. Start your agent

```bash
# Start a session with your agent in a Daily room
pcc agent start pipecat-test-agent --use-daily
```

or record video:

This will return a URL, which you can use to connect to your running agent.

```bash
pcc agent start pipecat-test-agent --use-daily --daily-properties '{"enable_recording": "cloud"}'
```

Using custom S3 bucket:

```bash
pcc agent start pipecat-test-agent --use-daily --daily-properties \
 '{"enable_recording": "cloud", "recordings_bucket": { "bucket_name": "your-bucket-name", "bucket_region": "us-west-2", "assume_role_arn": "arn:aws:iam::123456789012:role/your-role", "allow_api_access": true }, "transcription_bucket": { "bucket_name": "your-bucket-name", "bucket_region": "us-west-2", "assume_role_arn": "arn:aws:iam::123456789012:role/your-role", "allow_api_access": true }}'
```

### 7. Check the recorded video

```
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $DAILY_API_KEY" \
     https://api.daily.co/v1/recordings
```

```
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_KEY" \
     https://api.daily.co/v1/recordings/33282639-be65-4259-8759-dfae183acf37

     {"id":"33282639-be65-4259-8759-dfae183acf37","room_name":"WCSU8hYZEqZ4Q3gozin1","start_ts":1751356291,"status":"finished","max_participants":2,"duration":63,"share_token":"QmAikMMERxCM","tracks":[],"s3key":"cloud-241a97110f7042e9b45c7218a9778611/WCSU8hYZEqZ4Q3gozin1/1751356291783","mtgSessionId":"8eaa662e-bff1-4831-8f37-e52c410ab926","isVttEnabled":false}
```

```
curl -H "Content-Type: application/json" \
     -H "Authorization: Bearer $API_KEY" \
     https://api.daily.co/v1/recordings/0cb313e1-211f-4be0-833d-8c7305b19902/access-link
```

## Agent Launcher CLI

The project includes an `agent_launcher.py` script that provides a convenient CLI for launching agents with custom configurations:

```bash
# Launch agent with default settings
python agent_launcher.py

# Launch agent with custom name and data
python agent_launcher.py --agent-name test-agent --data='{"key": "hello"}'

# Launch agent with complex data
python agent_launcher.py --agent-name my-agent --data='{"user_id": "123", "context": "support"}'
```

### CLI Options

- `--agent-name`: Name of the agent to launch (defaults to "recruiter")
- `--data`: JSON data to pass to the agent session

This launcher automatically configures recording and transcription using your S3 bucket settings from environment variables.

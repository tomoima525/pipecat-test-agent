#!/bin/bash

# Docker build and push script for Pipecat Cloud Voice Agent
# Usage: ./build_and_push.sh <version> [docker_username]
# Example: ./build_and_push.sh 0.5 tomoima525

set -e

# Check if version is provided
if [ $# -eq 0 ]; then
    echo "Error: Version is required"
    echo "Usage: $0 <version> [docker_username]"
    echo "Example: $0 0.5 tomoima525"
    exit 1
fi

VERSION=$1
DOCKER_USERNAME=${2:-tomoima525}
IMAGE_NAME="pipecat-test-agent"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "Building Docker image: ${FULL_IMAGE_NAME}"

# Build the Docker image for ARM64 (required for Pipecat Cloud)
docker build --platform=linux/arm64 -t ${IMAGE_NAME}:latest .

# Tag with version
docker tag ${IMAGE_NAME}:latest ${FULL_IMAGE_NAME}

echo "Pushing Docker image: ${FULL_IMAGE_NAME}"

# Push to Docker Hub
docker push ${FULL_IMAGE_NAME}

echo "Successfully built and pushed: ${FULL_IMAGE_NAME}"
echo ""
echo "To deploy to Pipecat Cloud, run:"
echo "pcc deploy ${IMAGE_NAME} ${FULL_IMAGE_NAME} --secrets ${IMAGE_NAME}-secrets"
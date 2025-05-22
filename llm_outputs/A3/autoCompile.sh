#!/bin/bash

set -euo pipefail

# Configurable variables
IMAGE_NAME="a3"
CONTAINER_WORKDIR="/app"
RECOMPILE_SCRIPT="./compile.sh"

# Step 1: Build the Docker image if not present
echo "Checking if Docker image '${IMAGE_NAME}' exists..."
if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
    echo "Docker image not found. Building '${IMAGE_NAME}'..."
    docker build -t "${IMAGE_NAME}" .
else
    echo "Docker image '${IMAGE_NAME}' already exists."
fi

# Step 2: Run the container with mounted volume
echo "Starting Docker container to compile the project..."

docker run --rm -it \
  -v "$(pwd)":/app \
  -w /app \
  a3 \
  ./compile.sh


echo "Compilation complete."


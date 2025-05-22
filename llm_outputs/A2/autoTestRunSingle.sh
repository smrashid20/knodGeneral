#!/bin/bash

set -euo pipefail

TEST_NAME="test_verify"
IMAGE_NAME="a2"
CONTAINER_WORKDIR="/app"

# Check if Docker image exists
if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
    echo "Docker image '${IMAGE_NAME}' not found. Building it..."
    docker build -t "${IMAGE_NAME}" .
else
    echo "Docker image '${IMAGE_NAME}' already exists."
fi

# Run the test inside Docker
echo "Running test '${TEST_NAME}' inside Docker..."
docker run --rm -it \
  -v "$(pwd)":${CONTAINER_WORKDIR} \
  -w ${CONTAINER_WORKDIR} \
  "${IMAGE_NAME}" \
  ./testRunSingle.sh

echo "Test '${TEST_NAME}' run complete."


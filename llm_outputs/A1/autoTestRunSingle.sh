#!/bin/bash

set -euo pipefail

# Check for test name argument
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <test_name>"
    echo "Example: $0 15-test_rsa"
    exit 1
fi

TEST_NAME="test_evp_extra"
IMAGE_NAME="a1"
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
  ./testRunSingle.sh "${TEST_NAME}"

echo "Test '${TEST_NAME}' run complete."


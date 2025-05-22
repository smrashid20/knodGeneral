#!/bin/bash

set -euo pipefail

IMAGE_NAME="sb20"
CONTAINER_WORKDIR="/app"

echo "Running tests inside Docker container..."
docker run --rm -it \
  -v "$(pwd)":${CONTAINER_WORKDIR} \
  -w ${CONTAINER_WORKDIR} \
  "${IMAGE_NAME}" \
  ./testRunAll.sh

echo "Docker test run complete."


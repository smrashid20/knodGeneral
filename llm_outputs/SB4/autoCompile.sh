#!/bin/bash

set -euo pipefail

IMAGE_NAME="sb4"
CONTAINER_WORKDIR="/app"

echo "Checking if Docker image '${IMAGE_NAME}' exists..."
if ! docker image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
    echo "Docker image not found. Building '${IMAGE_NAME}'..."
    docker build -t "${IMAGE_NAME}" .
else
    echo "Docker image '${IMAGE_NAME}' already exists."
fi

echo "Running compilation in Docker container..."
docker run --rm -it \
  -v "$(pwd)":${CONTAINER_WORKDIR} \
  -w ${CONTAINER_WORKDIR} \
  "${IMAGE_NAME}" \
  ./compile.sh

echo "Done."


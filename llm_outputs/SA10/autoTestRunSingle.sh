#!/bin/bash

set -euo pipefail

IMAGE_NAME="sa10"
CONTAINER_WORKDIR="/app"
TEST_NAME="${1:-X509CrtParserTest#testMatchingParams}"

echo "Running single test inside Docker: ${TEST_NAME}"

docker run --rm -it \
  -v "$(pwd)":${CONTAINER_WORKDIR} \
  -w ${CONTAINER_WORKDIR} \
  "${IMAGE_NAME}" \
  ./testRunSingle.sh "${TEST_NAME}"

echo "Docker single test run complete."


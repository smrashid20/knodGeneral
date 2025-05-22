#!/bin/bash

set -euo pipefail

IMAGE_NAME="sc3"
CONTAINER_WORKDIR="/app"
TEST_NAME="${1:-AclFileTest#testCase_AclFileButNoRules}"

echo "Running single test inside Docker: ${TEST_NAME}"

docker run --rm -it \
  -v "$(pwd)":${CONTAINER_WORKDIR} \
  -w ${CONTAINER_WORKDIR} \
  "${IMAGE_NAME}" \
  ./testRunSingle.sh "${TEST_NAME}"

echo "Docker single test run complete."


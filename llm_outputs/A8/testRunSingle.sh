#!/bin/bash

set -euo pipefail

TEST_NAME="torture_rekey"
CUR_DIR="$(pwd)"
LOG_FILE="${CUR_DIR}/make_test_output.txt"

# Navigate to the build directory
cd build

echo "Running libssh test: ${TEST_NAME} ..."
ctest -R "${TEST_NAME}" --output-on-failure 2>&1 | tee -a "${LOG_FILE}" || {
    echo "Error: Test '${TEST_NAME}' failed. See log: ${LOG_FILE}"
    exit 1
}

echo "libssh test '${TEST_NAME}' completed successfully."
echo "Test log: ${LOG_FILE}"


#!/bin/bash

set -euo pipefail

# Check for test name argument
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <test_name>"
    echo "Example: $0 15-test_rsa"
    exit 1
fi

TEST_NAME="$1"
CUR_DIR="$(pwd)"

cd build

echo "Running OpenSSL test: ${TEST_NAME} ..."
make test TESTS="${TEST_NAME}" 2>&1 | tee -a "${CUR_DIR}/make_test_output.txt" || {
    echo "Error: Test '${TEST_NAME}' failed. Check ${CUR_DIR}/make_test_output.txt for details."
    exit 1
}

echo "OpenSSL test '${TEST_NAME}' completed successfully."
echo "Test log: ${CUR_DIR}/make_test_output.txt"


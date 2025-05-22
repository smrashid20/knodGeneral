#!/bin/bash

set -euo pipefail

# Set current directory and log file
CUR_DIR="$(pwd)"
LOG_FILE="${CUR_DIR}/make_test_output.txt"

echo "Entering test directory: tests"
cd "${CUR_DIR}/tests"

# Check if test binary exists
if [[ ! -x "./dtls_hello_random_value" ]]; then
    echo "Test binary not found. Running make check to build it..."
    cd "${CUR_DIR}"
    make check
    cd "${CUR_DIR}/tests"
fi

# ===============================
# Run the test
# ===============================
echo "Running test: ./dtls_hello_random_value"
./dtls_hello_random_value 2>&1 | tee "${LOG_FILE}" | {
    if grep -q "the client random value seems uninitialized"; then
        echo "Result: FAIL" | tee -a "${LOG_FILE}"
        exit 1
    else
        echo "Result: PASS" | tee -a "${LOG_FILE}"
    fi
}


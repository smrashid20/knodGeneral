#!/bin/bash

set -euo pipefail

CUR_DIR="$(pwd)"

echo "Running mbedtls test:  ..."
make check 2>&1 | tee -a "${CUR_DIR}/make_test_output.txt" || {
    echo "Error: Test failed. Check ${CUR_DIR}/make_test_output.txt for details."
    exit 1
}

echo "mbedtls test completed successfully."
echo "Test log: ${CUR_DIR}/make_test_output.txt"


#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Set the current directory
export CUR_DIR=$(pwd)

cd projects
cd openssl
cd build


# Run tests
echo "Running tests..."
make test 2>&1 | tee -a "${CUR_DIR}/make_test_output.txt" || {
    echo "Error: Tests failed. Check ${CUR_DIR}/make_test_output.txt for details."
    exit 1
}

# Success message
echo "OpenSSL has been successfully tested."
echo "Test log: ${CUR_DIR}/make_test_output.txt"

#!/bin/bash

set -euo pipefail

# Save current directory
CUR_DIR="$(pwd)"

# Output file
OUTPUT_FILE="${CUR_DIR}/make_test_output.txt"

# Clear previous test log if exists
> "$OUTPUT_FILE"

# Go to test directory
echo "Entering test/broker directory..." | tee -a "$OUTPUT_FILE"
cd test/broker

# Run the test, output both to screen and log
echo "Running test: 09-acl-empty-file.py" | tee -a "$OUTPUT_FILE"
python2 ./09-acl-empty-file.py 2>&1 | tee -a "$OUTPUT_FILE" || true

echo "" | tee -a "$OUTPUT_FILE"

# Check the file for any 'FAIL:' lines
if grep -q '^FAIL:' "$OUTPUT_FILE"; then
    echo "Result: FAIL" | tee -a "$OUTPUT_FILE"
    sleep 0.1
    exit 1
else
    echo "Result: PASS" | tee -a "$OUTPUT_FILE"
    exit 0
fi


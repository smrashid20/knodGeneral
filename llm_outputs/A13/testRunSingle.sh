#!/bin/bash

set -euo pipefail

# Set the current working directory
CUR_DIR="$(pwd)"

# ===============================
# Step 2: Run dlzexternal system test
# ===============================
echo "Entering system test directory..."
cd ./bin/tests/system

# Bring up test interfaces
echo "Setting up test network interface..."
sudo sh ifconfig.sh down
sudo sh ifconfig.sh up || {
    echo "Error: Failed to bring up test interface."
    exit 1
}

# Run the test
echo "Running BIND 9 system test: dlzexternal ..."
./run.sh dlzexternal 2>&1 | tee -a "${CUR_DIR}/make_test_output.txt" || {
    echo "dlzexternal test failed. Check the log for details."
    exit 1
}

echo "dlzexternal test completed successfully."
echo "Test log: ${CUR_DIR}/make_test_output.txt"


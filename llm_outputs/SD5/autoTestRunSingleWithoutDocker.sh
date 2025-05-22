#!/bin/bash

set -euo pipefail

if ! command -v java &>/dev/null; then
    echo "Error: 'java' not found. Please install it before continuing."
    exit 1
fi

TEST_NAME="${1:-AdminManagerPrivilegeEscalationTest#testInitializeCipher_KeyIvLengthPersistence}"

echo "Running single test locally: ${TEST_NAME}"

chmod +x ./testRunSingle.sh
./testRunSingle.sh "${TEST_NAME}"

echo "Local single test run complete."


#!/bin/bash

set -euo pipefail

# Ensure required tools are available
if ! command -v java &>/dev/null; then
    echo "Error: 'java' not found. Please install it before continuing."
    exit 1
fi

echo "Running tests locally..."
chmod +x ./testRunAll.sh
./testRunAll.sh

echo "Local test run complete."


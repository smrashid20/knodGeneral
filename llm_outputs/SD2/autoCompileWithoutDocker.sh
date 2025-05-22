#!/bin/bash

set -euo pipefail

# Check if javac is available
if ! command -v javac &>/dev/null; then
    echo "Error: javac not found. Please install JDK 7 or higher."
    exit 1
fi

# Check if wget is available
if ! command -v wget &>/dev/null; then
    echo "Error: wget not found. Please install wget."
    exit 1
fi

# Run the standard compile script
echo "Running compile.sh without Docker..."
chmod +x ./compile.sh
./compile.sh

echo "Local compilation complete."


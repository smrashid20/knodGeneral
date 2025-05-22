#!/bin/bash

set -e  # Exit immediately on error
set -u  # Treat unset variables as an error

# Get absolute path to the project root
export CUR_DIR="$(cd "$(dirname "$0")" && pwd)"

# Configure the build
echo "Configuring BIND 9..."
PYTHON=python3 "${CUR_DIR}/configure" || {
    echo "Error: Configuration failed."
    exit 1
}

# Build BIND 9
echo "Building BIND 9..."
make -j"$(nproc)" 2>&1 | tee -a "${CUR_DIR}/make_output.txt" || {
    echo "Error: Build failed. Check ${CUR_DIR}/make_output.txt for details."
    exit 1
}

echo "Build completed successfully."
echo "Build log: ${CUR_DIR}/make_output.txt"


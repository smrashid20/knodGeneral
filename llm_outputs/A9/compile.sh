#!/bin/bash

set -e  # Exit on error
set -u  # Treat unset vars as errors

# Get absolute path to project root
export CUR_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$CUR_DIR"

echo "Running bootstrap..."
./bootstrap

echo "Configuring..."
./configure

echo "Building GnuTLS with $(nproc) cores..."
make -j"$(nproc)" 2>&1 | tee make_output.txt

echo "Build completed successfully!"
echo "Build log saved to: ${CUR_DIR}/make_output.txt"


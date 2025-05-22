#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Set the current directory
export CUR_DIR=$(pwd)

cd projects
cd openssl

# Create and navigate to the build directory
echo "Setting up build environment..."
mkdir -p build
cd build

# Configure the build
echo "Configuring the build..."
../Configure --prefix=$(pwd)/install || {
    echo "Error: Configuration failed."
    exit 1
}

# Build OpenSSL
echo "Building OpenSSL..."
make -j$(nproc) 2>&1 | tee -a "${CUR_DIR}/make_output.txt" || {
    echo "Error: Build failed. Check ${CUR_DIR}/make_output.txt for details."
    exit 1
}

# Success message
echo "OpenSSL has been successfully built."
echo "Build log: ${CUR_DIR}/make_output.txt"
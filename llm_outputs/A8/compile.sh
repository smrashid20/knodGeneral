#!/bin/bash

set -e  # Exit on error
set -u  # Treat unset variables as errors

# Absolute path to project root
export CUR_DIR="$(cd "$(dirname "$0")" && pwd)"

# Build and install dirs
BUILD_DIR="${CUR_DIR}/build"
INSTALL_DIR="${BUILD_DIR}/install"
LOG_FILE="${CUR_DIR}/make_output.txt"

# Clean up old logs
rm -f "${LOG_FILE}"

# Make sure build directory exists
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

# Configure the build
echo "Configuring the build..."
cmake \
  -DCLIENT_TESTING=ON \
  -DUNIT_TESTING=ON \
  -DWITH_GSSAPI=OFF \
  -DWITH_NACL=OFF \
  -DWITH_ABI_BREAK=OFF \
  -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
  .. || {
    echo "Error: Configuration failed."
    exit 1
}

# Compile the project
echo "Building libssh..."
make -j"$(nproc)" 2>&1 | tee -a "${LOG_FILE}" || {
    echo "Error: Build failed. Check ${LOG_FILE} for details."
    exit 1
}


echo "Build complete."
echo "Build log: ${LOG_FILE}"


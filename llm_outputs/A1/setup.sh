#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
set -u  # Treat unset variables as an error

# Set the current directory
export CUR_DIR=$(pwd)

# Ensure 'projects' directory exists
if [ ! -d projects ]; then
    echo "Creating 'projects' directory."
    mkdir projects
fi

cd projects

# Clean up any existing OpenSSL directory and clone the repository
echo "Cloning OpenSSL repository..."
rm -rf openssl
git clone https://github.com/openssl/openssl.git || {
    echo "Error: Failed to clone OpenSSL repository."
    exit 1
}

cd openssl

# Checkout the specified commit
COMMIT_HASH="f3a7e6c057b5054aa05710f3d528b92e3e885268"
echo "Checking out commit $COMMIT_HASH..."
git checkout "$COMMIT_HASH" || {
    echo "Error: Failed to checkout commit $COMMIT_HASH."
    exit 1
}
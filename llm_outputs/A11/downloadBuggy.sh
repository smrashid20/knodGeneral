#!/bin/bash

# Script to clone Mbed TLS into ./projects and checkout a specific commit

# Hardcoded values
REPO_URL="https://github.com/Mbed-TLS/mbedtls.git"
COMMIT_HASH="c60c30eb68dd70c71f902f55eb0db69b466e7503"
TARGET_DIR="${1:-./projects}"

# Remove existing target directory if it exists
if [ -d "$TARGET_DIR" ]; then
  echo "Removing existing directory: $TARGET_DIR"
  rm -rf "$TARGET_DIR"
fi

# Clone the repo directly into projects/
echo "Cloning Mbed TLS into: $TARGET_DIR"
git clone "$REPO_URL" "$TARGET_DIR"

# Check if clone was successful
if [ $? -ne 0 ]; then
  echo "Failed to clone repository."
  exit 2
fi

# Change into the cloned directory
cd "$TARGET_DIR" || { echo "Failed to change directory."; exit 3; }

# Checkout the specified commit
git checkout "$COMMIT_HASH"
if [ $? -ne 0 ]; then
  echo "Failed to checkout commit."
  exit 4
fi

echo "Repository cloned, checked out to commit $COMMIT_HASH, and all submodules initialized successfully."

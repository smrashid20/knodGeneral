#!/bin/bash

# Script to clone Mbed TLS into ./projects and checkout a specific commit

# Hardcoded values
REPO_URL="https://github.com/Mbed-TLS/mbedtls.git"
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

# Initialize submodules
echo "Initializing submodules (top level)..."
git submodule update --init

# Navigate to tf-psa-crypto and init its submodules
TF_DIR="tf-psa-crypto"
if [ -d "$TF_DIR" ]; then
  echo "Entering $TF_DIR to update submodules..."
  cd "$TF_DIR" || { echo "Failed to enter tf-psa-crypto directory."; exit 5; }
  git submodule update --init
  cd - > /dev/null  # Return to original directory, suppress output
else
  echo "tf-psa-crypto directory not found: $TF_DIR"
  exit 6
fi

echo "Repository cloned, checked out to commit $COMMIT_HASH, and all submodules initialized successfully."

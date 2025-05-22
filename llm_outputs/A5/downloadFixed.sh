#!/bin/bash

# Script to clone OpenSSL into ./projects and checkout a specific commit

# Hardcoded values
REPO_URL="https://github.com/openssl/openssl.git"
COMMIT_HASH="6ee1f4f40b5100ef2744866a727bb4b9ef8ea39e"
TARGET_DIR="${1:-./projects}"

# Remove existing target directory if it exists
if [ -d "$TARGET_DIR" ]; then
  echo "Removing existing directory: $TARGET_DIR"
  rm -rf "$TARGET_DIR"
fi

# Clone the repo directly into projects/
echo "Cloning OpenSSL into: $TARGET_DIR"
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

# Check if checkout was successful
if [ $? -ne 0 ]; then
  echo "Failed to checkout commit."
  exit 4
fi

echo "Repository cloned directly into '$TARGET_DIR' and checked out to commit $COMMIT_HASH."


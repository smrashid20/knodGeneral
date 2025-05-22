#!/bin/bash

# Script to clone libssh into ./projects and checkout a specific commit

# Hardcoded values
REPO_URL="https://github.com/openssh/openssh-portable.git"
COMMIT_HASH="47aa7a0f8551b471fcae0447c1d78464f6dba869"
TARGET_DIR="${1:-./projects}"

# Remove existing target directory if it exists
if [ -d "$TARGET_DIR" ]; then
  echo "Removing existing directory: $TARGET_DIR"
  rm -rf "$TARGET_DIR"
fi

# Clone the repo directly into projects/
echo "Cloning libssh into: $TARGET_DIR"
git clone "$REPO_URL" "$TARGET_DIR"

# Check if clone was successful
if [ $? -ne 0 ]; then
  echo "Failed to clone repository."
  exit 2
fi

# Change into the cloned directory
cd "$TARGET_DIR" || { echo "Failed to change directory."; exit 3; }

# Checkout the specified commit
echo "Checking out commit: $COMMIT_HASH"
git checkout "$COMMIT_HASH"

# Check if checkout was successful
if [ $? -ne 0 ]; then
  echo "Failed to checkout commit."
  exit 4
fi

echo "libssh cloned into '$TARGET_DIR' and checked out to commit $COMMIT_HASH."


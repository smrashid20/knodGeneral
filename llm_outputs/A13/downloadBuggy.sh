#!/bin/bash

# Script to clone libssh into ./projects and checkout a specific commit

# Hardcoded values
REPO_URL="https://gitlab.isc.org/isc-projects/bind9.git"
COMMIT_HASH="5e7f1a8d679c33979ecaf25471a556b145f1a262"
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

echo "Bind9 cloned into '$TARGET_DIR' and checked out to commit $COMMIT_HASH."


#!/bin/bash

# Hardcoded values
REPO_URL="https://github.com/vadz/libtiff.git"
COMMIT_HASH="Release-v4-0-6"
TARGET_DIR="${1:-./projects}"

# Determine the directory this script resides in
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Remove existing target directory if it exists
if [ -d "$TARGET_DIR" ]; then
  echo "Removing existing directory: $TARGET_DIR"
  rm -rf "$TARGET_DIR"
fi

# Clone the repo directly into projects/
echo "Cloning libtiff into: $TARGET_DIR"
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

cp "$SCRIPT_DIR/gif2tiff.c" "./tools/gif2tiff.c"

if [ $? -ne 0 ]; then
  echo "Failed to copy gif2tiff.c to $TOOLS_DIR."
  exit 5
fi

echo "Repository cloned into '$TARGET_DIR', checked out to '$COMMIT_HASH', and gif2tiff.c copied to '$TOOLS_DIR/'."

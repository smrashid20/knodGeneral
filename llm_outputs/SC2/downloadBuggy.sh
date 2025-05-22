#!/bin/bash

set -euo pipefail

SOURCE_DIR="../SyntheticDataset/SC2/SC2_buggy"
TARGET_DIR="./projects"

# Clean up target if it exists
if [ -d "$TARGET_DIR" ]; then
  echo "Removing existing '$TARGET_DIR' directory..."
  rm -rf "$TARGET_DIR"
fi

# Create target directory
mkdir -p "$TARGET_DIR"

# Copy contents from the source folder
echo "Copying contents from '$SOURCE_DIR' to '$TARGET_DIR'..."
cp -r "$SOURCE_DIR/"* "$TARGET_DIR/"

echo "Buggy project copied to '$TARGET_DIR'."


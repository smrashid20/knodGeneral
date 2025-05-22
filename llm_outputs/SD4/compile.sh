#!/bin/bash

set -euo pipefail

# Get absolute path
CUR_DIR="$(cd "$(dirname "$0")" && pwd)"

# Clean previous outputs
rm -rf "${CUR_DIR}/out" "${CUR_DIR}/lib"

# Create lib directory and download dependencies
mkdir -p "${CUR_DIR}/lib"
wget -P "${CUR_DIR}/lib" https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar
wget -P "${CUR_DIR}/lib" https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar

# Compile sources and tests
mkdir -p "${CUR_DIR}/out"
find "${CUR_DIR}/src" "${CUR_DIR}/test" -name "*.java" > sources.txt
javac -cp "${CUR_DIR}/lib/*" -d "${CUR_DIR}/out" @sources.txt

echo "Compilation complete. Output in ${CUR_DIR}/out"


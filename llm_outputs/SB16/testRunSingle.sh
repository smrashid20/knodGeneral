#!/bin/bash

set -euo pipefail

CUR_DIR="$(cd "$(dirname "$0")" && pwd)"

TEST_NAME="${1:-LookupFrecTest#testDoesNotMatchWithWrongFd}"

echo "Running single test: ${TEST_NAME}"

rm -rf "${CUR_DIR}/out"
rm -rf "${CUR_DIR}/lib"

mkdir -p "${CUR_DIR}/lib"
wget -P "${CUR_DIR}/lib" https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar
wget -P "${CUR_DIR}/lib" https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar

mkdir -p "${CUR_DIR}/out"
javac -cp .:"${CUR_DIR}/lib/*" -d "${CUR_DIR}/out" $(find src test -name "*.java")

java -cp "${CUR_DIR}/out:${CUR_DIR}/lib/*" SingleJUnitTestRunner "${TEST_NAME}"

echo "Single test run complete."


#!/bin/bash

set -e

git config --global --add safe.directory /Openfire

# Clean and build using Maven
echo "[*] Building Openfire..."
./mvnw verify -pl distribution -am

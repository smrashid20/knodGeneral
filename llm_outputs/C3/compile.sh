#!/bin/bash

# Exit on any error
set -e

# Compile
make -j$(nproc)


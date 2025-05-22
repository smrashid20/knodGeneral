#!/bin/bash
set -e

# -----------------------------------
# Configure the build
# -----------------------------------
./configure --prefix=/usr/local/proftpd --enable-openssl

# -----------------------------------
# Build and install
# -----------------------------------
make -j$(nproc)
# -----------------------------------
# Done
# -----------------------------------
echo "[✓] ProFTPD built and installed to /usr/local/proftpd"

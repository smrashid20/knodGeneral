#!/bin/bash
set -euo pipefail

echo "[*] Running autogen.sh..."
./autogen.sh

echo "[*] Running configure..."
./configure

echo "[*] Building wolfSSL..."
make -j"$(nproc)"

echo "wolfSSL build and installation complete."

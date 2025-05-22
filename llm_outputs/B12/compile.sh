#!/bin/bash
set -euo pipefail

echo "[*] Running autogen.sh..."
./autogen.sh

echo "[*] Running configure..."
./configure

echo "[*] Building wolfSSL..."
make CFLAGS="$CFLAGS -Wno-error=maybe-uninitialized -Wno-error=strict-prototypes" -j"$(nproc)"


echo "wolfSSL build and installation complete."

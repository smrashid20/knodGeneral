#!/bin/bash
set -euo pipefail

# -------------------------------------------------------------------------
# Build process
# -------------------------------------------------------------------------
echo "[*] Running autoreconf..."
autoreconf -fi

echo "[*] Configuring build..."
./configure --without-python

echo "[*] Building Bind9..."
make -j"$(nproc)"

echo "[*] Installing Bind9..."


#!/bin/bash
set -euo pipefail

# -------------------------------------------------------------------------
# Build process
# -------------------------------------------------------------------------
echo "[*] Running autoreconf..."
autoreconf -fi

echo "[*] Configuring build..."
./configure

echo "[*] Building Bind9..."
make -j"$(nproc)"


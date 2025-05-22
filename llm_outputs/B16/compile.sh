#!/bin/bash
set -e

# -----------------------------------
# Clean previous builds if any
# -----------------------------------
make clean || true

# -----------------------------------
# Build dnsmasq
# -----------------------------------
make -j$(nproc)

# -----------------------------------
# Done
# -----------------------------------
echo "[✓] dnsmasq built successfully."

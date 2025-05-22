#!/bin/bash
set -e

export PREFIX="/usr/local/gnutls"

# Redirect the OpenSSL submodule to the GitHub mirror
git config --global \
  url."https://github.com/openssl/openssl.git".insteadOf \
  git://git.openssl.org/openssl.git

# Mark directories as safe under root
git config --global --add safe.directory /gnutls
git config --global --add safe.directory /gnutls/devel/openssl

# Remove the broken tlsproxy submodule
git submodule deinit -f doc/examples/tlsproxy 2>/dev/null || true
rm -rf .git/modules/doc/examples/tlsproxy doc/examples/tlsproxy

# Initialize remaining top‑level submodules
git submodule update --init

# Bootstrap (will pull in openssl, nettle, libtasn1, unistring, etc.)
make bootstrap

# Optional: install unbound-anchor to satisfy DNSSEC root key requirement
if ! command -v unbound-anchor &>/dev/null; then
  echo "→ Installing unbound-anchor to generate DNSSEC root key"
  apt-get update
  apt-get install -y --no-install-suggests --no-install-recommends unbound-anchor
  unbound-anchor -a /etc/unbound/root.key
fi

# Choose a custom prefix so you don't clobber your system libs
NETTLE_PREFIX="/opt/nettle-3.7.2"

# Fetch, unpack
cd /tmp
wget https://ftp.gnu.org/gnu/nettle/nettle-3.7.2.tar.gz
tar xf nettle-3.7.2.tar.gz
cd nettle-3.7.2

# Configure & install
./configure \
  --prefix="$NETTLE_PREFIX" \
  --disable-static    \
  --enable-shared

# ./configure \
#     --prefix="$PREFIX" \
#     --disable-static \
#     --enable-shared \
#     --with-default-trust-store-pkcs11="pkcs11:"


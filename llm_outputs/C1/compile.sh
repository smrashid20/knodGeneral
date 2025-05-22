./config \
    --prefix=/usr/local/openssl-$OPENSSL_VERSION \
    --openssldir=/usr/local/openssl-$OPENSSL_VERSION \
    no-shared zlib \
    enable-deprecated

# Build and install
make -j"$(nproc)"
# Optionally link or export environment variables
echo "OpenSSL $OPENSSL_VERSION has been installed to /usr/local/openssl-$OPENSSL_VERSION"

# Set environment variables to use this OpenSSL build (optional)
echo "To use this build, export the following variables:"
echo "  export PATH=/usr/local/openssl-$OPENSSL_VERSION/bin:\$PATH"
echo "  export LD_LIBRARY_PATH=/usr/local/openssl-$OPENSSL_VERSION/lib:\$LD_LIBRARY_PATH"
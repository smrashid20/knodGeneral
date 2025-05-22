./config \
    --prefix=/usr/local/openssl-$OPENSSL_VERSION \
    --openssldir=/usr/local/openssl-$OPENSSL_VERSION \
    no-shared zlib

# Build and install
make -j"$(nproc)"

# Set environment variables to use this OpenSSL build (optional)
echo "To use this build, export the following variables:"
echo "  export PATH=/usr/local/openssl-$OPENSSL_VERSION/bin:\$PATH"
echo "  export LD_LIBRARY_PATH=/usr/local/openssl-$OPENSSL_VERSION/lib:\$LD_LIBRARY_PATH"
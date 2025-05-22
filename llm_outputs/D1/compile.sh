# Build pjproject
./configure CFLAGS="-fPIC"
make dep && make clean
make -j"$(nproc)"
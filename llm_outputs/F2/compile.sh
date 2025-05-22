#!/usr/bin/env bash
set -euo pipefail

# CONFIGURATION
PROJECT_ID="libtiff"
BUG_ID="CVE-2014-8128"
FILEPATH_X="tools/thumbnail.c"

IMAGE_NAME="extractfix-benchmark"
CONTAINER_NAME="efb-run-${PROJECT_ID}-${BUG_ID}"

# 1) Build the Docker image if it doesn't already exist
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
  echo "Building Docker image '$IMAGE_NAME'..."
  docker build -t "$IMAGE_NAME" .
else
  echo "Docker image '$IMAGE_NAME' already exists."
fi

# 2) Remove any existing container with the same name
if docker ps -a --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
  echo "Removing existing container '$CONTAINER_NAME'..."
  docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true
  docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true
fi

# 3) Start a new disposable container
echo "Starting container '$CONTAINER_NAME'..."
docker run -d --name "$CONTAINER_NAME" "$IMAGE_NAME" tail -f /dev/null

# 4) Inside the container: clone the benchmark repo if needed
echo "Cloning extractfix-benchmark inside container..."
docker exec "$CONTAINER_NAME" bash -c "
  if [ ! -d /extractfix-benchmark ]; then
    git clone https://github.com/nus-apr/extractfix-benchmark.git /extractfix-benchmark
  else
    echo '/extractfix-benchmark already exists, skipping clone'
  fi
"

# 5) Copy local test.sh into the container’s bug directory
echo "Copying test.sh into container..."
docker cp test.sh "${CONTAINER_NAME}":/extractfix-benchmark/${PROJECT_ID}/${BUG_ID}/test.sh || true

# 6) Inside the container: run setup.sh and config.sh
echo "Running setup and config inside container..."
docker exec "$CONTAINER_NAME" bash -c "
  cd /extractfix-benchmark/${PROJECT_ID}/${BUG_ID} && \
  chmod +x setup.sh && ./setup.sh && \
  chmod +x config.sh && ./config.sh
"

# 7) Copy your patched source file into the experiment directory
echo "Copying '$FILEPATH_X' into container experiment..."
docker cp "$FILEPATH_X" "${CONTAINER_NAME}":/experiment/extractfix-benchmark/${PROJECT_ID}/${BUG_ID}/src/${FILEPATH_X} || true

# 8) Build inside the container, capture output to host file
echo "Building project inside container..."
docker exec "$CONTAINER_NAME" bash -c "
  cd /extractfix-benchmark/${PROJECT_ID}/${BUG_ID} && \
  chmod +x build.sh && ./build.sh
" > make_output.txt 2>&1

echo "Build output written to make_output.txt"

# 10) Cleanup
echo "Stopping and removing container..."
docker stop "$CONTAINER_NAME" > /dev/null 2>&1 || true

docker rm "$CONTAINER_NAME" > /dev/null 2>&1 || true

echo "Done."

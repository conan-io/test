#!/usr/bin/env bash

set -e

# Determine the current directory
CURRENT_DIR="$(pwd)"

# Set ROOT_DATA_DIR based on current directory and Artifactory version
ROOT_DATA_DIR="${CURRENT_DIR}/artifactory_data"

rm -rf "${ROOT_DATA_DIR}"

# Create the data directory and necessary subdirectories
mkdir -p "${ROOT_DATA_DIR}/var/etc"

# Copy system.yaml to the data directory
cp ./artifactory/system.yaml "${ROOT_DATA_DIR}/var/etc/system.yaml"

# Set ownership to UID 1030 and GID 1030
chown -R 1030:1030 "${ROOT_DATA_DIR}/var"

ls -la "${ROOT_DATA_DIR}/var/etc/system.yaml"

chmod -R 777 "${ROOT_DATA_DIR}"

# Export ROOT_DATA_DIR for docker-compose
export ROOT_DATA_DIR

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install docker-compose
pip install "docker==6.1.3"

# Function to compare versions
function version_gt() { 
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

min_artifactory_version="6.9.0"
if version_gt "$min_artifactory_version" "$ARTIFACTORY_VERSION"; then
    echo "Artifactory version $ARTIFACTORY_VERSION does not support Conan revisions, exiting successfully."
    exit 0
fi

echo "Building Docker containers..."
docker-compose build
docker-compose pull

echo "Starting Docker containers and running tests..."
# Run docker-compose up and capture the exit code
if docker-compose up --abort-on-container-exit; then
    echo "Tests passed!"
    docker-compose down
    exit 0
else
    echo "Tests failed or Artifactory failed to start."
    echo "Fetching Artifactory logs..."
    docker-compose logs artifactory
    docker-compose down
    exit 99
fi

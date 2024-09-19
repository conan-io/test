#!/usr/bin/env bash

set -e

# Determine the current directory
CURRENT_DIR="$(pwd)"

# Set ROOT_DATA_DIR based on current directory and Artifactory version
ROOT_DATA_DIR="${CURRENT_DIR}/artifactory_data/${ARTIFACTORY_VERSION}"

# Create the data directory if it doesn't exist
mkdir -p "${ROOT_DATA_DIR}/var/etc"

# Copy system.yaml to the data directory
cp ./artifactory/system.yaml "${ROOT_DATA_DIR}/var/etc/system.yaml"

# Set ownership to UID 1030 and GID 1030
chown -R 1030:1030 "${ROOT_DATA_DIR}/var"

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
    deactivate
    exit 0
fi

echo "Building Docker containers..."
docker-compose build
docker-compose pull

echo "Starting Docker containers..."
docker-compose up -d

# Run tests
if docker-compose run test_runner ./launch.sh; then
    echo "Tests passed!"
    docker-compose down
    deactivate
    exit 0
else
    echo "Tests failed!"
    docker-compose down
    deactivate
    exit 99
fi

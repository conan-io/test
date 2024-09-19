#!/usr/bin/env bash

set -e

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
docker-compose up -d
if docker-compose run test_runner ./launch.sh; then
    echo "Tests passed!"
    docker-compose down
    exit 0
else
    echo "Tests failed or Artifactory failed to start."
    docker-compose down
    exit 99
fi

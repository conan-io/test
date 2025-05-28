#!/usr/bin/env bash
set -e

pip install --upgrade pip

echo "Building Docker containers..."
docker compose build
docker compose pull

echo "Starting Docker containers and running tests..."
docker compose up -d
if docker compose run test_runner ./launch.sh; then
    echo "Tests passed!"
    docker compose down
    exit 0
else
    echo "Tests failed or Artifactory failed to start."
    docker compose down
    exit 99
fi

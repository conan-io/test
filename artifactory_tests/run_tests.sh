#!/usr/bin/env bash

set -e
echo "Launching containers..."
docker-compose build
docker-compose up -d
if docker-compose run test_runner ./launch.sh; then
    echo "Tests OK!"
    docker-compose down
    exit 0
else
    echo "Tests Failed!"
    docker-compose down
    exit -1
fi

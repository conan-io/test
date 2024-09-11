#!/usr/bin/env bash

set -e

pip install docker-compose
pip install docker==6.1.3

function version_gt() { test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"; }
min_artifactory_version=6.9.0
if version_gt $min_artifactory_version $ARTIFACTORY_VERSION; then
     echo "Artifactory not supported for Conan revisions, exiting ok"
     exit 0
fi

echo "Building containers..."
docker-compose build
docker-compose pull
echo "Launching containers..."
docker-compose up -d
echo "Waiting for Artifactory to be ready..."

# Ensure that PostgreSQL and Artifactory are ready
until curl -uadmin:password http://localhost:8081/artifactory/api/system/ping --fail; do
   echo "Waiting for Artifactory to start..."
   sleep 5
done

if docker-compose run test_runner ./launch.sh; then
    echo "Tests OK!"
    docker-compose down
    exit 0
else
    echo "Tests Failed!"
    docker-compose down
    exit 99
fi

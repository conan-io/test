#!/usr/bin/env bash

set -e

# Remove existing virtual environment if it exists
if [ -d "tests-env" ]; then
    echo "Removing existing virtual environment..."
    rm -rf tests-env
fi

# Wait until Artifactory is ready
until curl -sSf -u"$ARTIFACTORY_USER:$ARTIFACTORY_PASSWORD" "$ARTIFACTORY_DEFAULT_URL/api/system/ping" > /dev/null
do
    echo "Artifactory not ready... waiting"
    sleep 4
done

echo "Artifactory responded OK!"

# Get Artifactory version
curl -u"$ARTIFACTORY_USER:$ARTIFACTORY_PASSWORD" -XGET "$ARTIFACTORY_DEFAULT_URL/api/system/version"

# Apply Artifactory license
curl -u"$ARTIFACTORY_USER:$ARTIFACTORY_PASSWORD" --output /dev/null -XPOST "$ARTIFACTORY_DEFAULT_URL/api/system/licenses" \
     -H "Content-type: application/json" \
     -d "{ \"licenseKey\" : \"$ART_LICENSE\"}"

# Clone Conan repository
echo "Cloning Conan repository..."
git clone "$CONAN_GIT_REPO" conan_sources
cd conan_sources
git checkout "$CONAN_GIT_TAG"

# Install Conan in editable mode
echo "Installing Conan in editable mode..."
python3 -m venv tests-env
source tests-env/bin/activate
pip install --upgrade pip
pip install -e . 
pip install -r conans/requirements_dev.txt 
pip install -r conans/requirements_server.txt 
pip install nose
pip list

# Run tests
echo "Running tests..."
if [ -d "conans/test" ]; then
    pytest conans/test -m "artifactory_ready"
elif [ -d "test" ]; then
    pytest test -m "artifactory_ready"
else
    echo "No test directory found"
    exit 1
fi

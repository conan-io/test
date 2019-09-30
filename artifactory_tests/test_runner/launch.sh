#!/usr/bin/env bash

set -e
until curl -v $ARTIFACTORY_DEFAULT_URL/api/system/ping --fail
do
   echo "Artifactory not ready... waiting"
   # curl -v $ARTIFACTORY_DEFAULT_URL/api/system/ping
   sleep 4
done

echo "Artifactory responded OK! let's clone Conan"
git clone $CONAN_GIT_REPO conan_sources
cd conan_sources
git checkout $CONAN_GIT_TAG
echo "Let's install Conan as editable"
pip3 install -e . && pip3 install -r conans/requirements_dev.txt
rm __init__.py
echo "Let's run the tests"
nosetests -w conans -A "artifactory_ready" -v
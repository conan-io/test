#!/usr/bin/env bash

set -e
until curl -I $ARTIFACTORY_DEFAULT_URL/api/system/ping --fail
do
   echo "Artifactory not ready... waiting"
   sleep 4
done

git clone $CONAN_GIT_REPO
cd conan
git checkout $CONAN_GIT_TAG
pip3 install -e . && pip3 install -r conans/requirements_dev.txt
nosetests conans.test.integration.revisions_test
#!/usr/bin/env bash

set -e

# Delete the existing virtual environment if it exists
if [ -d "tests-env" ]; then
   echo "Removing existing virtual environment..."
   rm -rf tests-env
fi

until curl -uadmin:password $ARTIFACTORY_DEFAULT_URL/api/system/ping --fail; do
   echo "Artifactory not ready... waiting"
   sleep 5
done

echo "Artifactory responded OK!"
curl -uadmin:password -XGET $ARTIFACTORY_DEFAULT_URL/api/system/version
curl -uadmin:password --output /dev/null -XPOST "$ARTIFACTORY_DEFAULT_URL/api/system/licenses" -H "Content-type: application/json" -d "{ \"licenseKey\" : \"$ART_LICENSE\"}"

echo "Let's clone Conan"
git clone $CONAN_GIT_REPO conan_sources
cd conan_sources
git checkout $CONAN_GIT_TAG

echo "Let's install Conan as editable"
python3 -m venv tests-env
source tests-env/bin/activate
pip3 install -e . && pip3 install -r conans/requirements_dev.txt && pip3 install -r conans/requirements_server.txt && pip3 install nose
pip3 list

# in develop we still have tests under conans/test and
# develop2 has them under test
echo "Let's run the tests"
if [ -d "conans/test" ]; then
    pytest conans/test -m "artifactory_ready"
elif [ -d "test" ]; then
    pytest test -m "artifactory_ready"
else
    echo "No test directory found"
    exit 1
fi

FROM ubuntu:latest
RUN apt-get update
RUN apt-get install -y git python3 python3-pip python3-venv curl subversion
ADD launch.sh launch.sh
RUN chmod +x launch.sh
ENV TESTING_REVISIONS_ENABLED="1"
ENV CONAN_TEST_WITH_ARTIFACTORY="1"
ENV ARTIFACTORY_DEFAULT_URL="http://artifactory:8081/artifactory"
ENV CONAN_GIT_REPO=$CONAN_GIT_REPO
ENV CONAN_GIT_TAG=$CONAN_GIT_TAG

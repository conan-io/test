ARG artifactory_version=latest
FROM releases-docker.jfrog.io/jfrog/artifactory-pro:${artifactory_version}
USER root
COPY system.yaml /opt/jfrog/artifactory/var/etc/system.yaml
RUN chown 1030:1030 /opt/jfrog/artifactory/var/etc/system.yaml
USER artifactory

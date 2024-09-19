FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    subversion \
    && rm -rf /var/lib/apt/lists/*

# Add and make launch.sh executable
ADD launch.sh /launch.sh
RUN chmod +x /launch.sh

# Set environment variables
ENV TESTING_REVISIONS_ENABLED="1" \
    CONAN_TEST_WITH_ARTIFACTORY="1" \
    ARTIFACTORY_DEFAULT_URL="http://artifactory:8081/artifactory"

# Set working directory
WORKDIR /test_runner

# Copy necessary files
COPY . .

# Set entrypoint
ENTRYPOINT ["/launch.sh"]

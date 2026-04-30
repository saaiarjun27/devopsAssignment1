# Custom Jenkins image with Docker CLI for ACEest Fitness pipeline
# Includes Docker CLI so the pipeline can run docker commands and
# spin up python:3.12-slim containers for testing stages.
FROM jenkins/jenkins:lts-jdk17

USER root

# Install Docker CLI (connects to the host Docker daemon via mounted socket)
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg lsb-release && \
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
    https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add jenkins user to the docker group so it can run docker commands
RUN groupadd -f docker && usermod -aG docker jenkins

USER jenkins

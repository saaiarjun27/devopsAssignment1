# Custom Jenkins image with Python 3 for ACEest Fitness pipeline
FROM jenkins/jenkins:lts

USER root

# Install Python 3, pip, and build essentials
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER jenkins

# --------------------------------------------------------
# Dockerfile for ACEest Fitness & Gym – Flask Application
# --------------------------------------------------------
# Multi-stage-ish slim build for size & security.
# Uses python:3.12-slim to minimise image footprint.
# --------------------------------------------------------

FROM python:3.12-slim

# Metadata
LABEL maintainer="saaiarjun27"
LABEL description="ACEest Fitness & Gym – Flask web application"
LABEL version="1.0"

# Security: create a non-root user
RUN groupadd -r aceest && useradd -r -g aceest aceest

# Set the working directory
WORKDIR /app

# Copy and install dependencies first (leverages Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY . .

# Change ownership to the non-root user
RUN chown -R aceest:aceest /app

# Switch to non-root user for runtime
USER aceest

# Expose the Flask port
EXPOSE 5000

# Health-check (used by orchestrators / Docker Compose)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Default command: run the Flask app
CMD ["python", "app.py"]

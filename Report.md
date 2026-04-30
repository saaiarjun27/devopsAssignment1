# DevOps Pipeline Report: ACEest Fitness & Gym Management

## 1. CI/CD Architecture Overview

The continuous integration and continuous deployment (CI/CD) architecture for the ACEest Fitness & Gym Management application is designed to be highly automated, scalable, and secure. The core of this pipeline is orchestrated using Jenkins and GitHub Actions.

### Key Components:
- **Version Control**: Git and GitHub are used to manage all source code, including application files (`app.py`), infrastructure as code (Dockerfile, Kubernetes manifests), and testing scripts. Branches and tagging are utilized to maintain clear version tracking across the incremental upgrades of the original `ACEest_Fitness.py` script.
- **Continuous Integration (Jenkins)**: 
  - **Triggers**: Jenkins is configured with webhooks to trigger pipeline builds automatically upon any push to the repository branches.
  - **Test Automation**: A robust testing suite designed with `pytest` is executed. The pipeline also features `pytest-cov` to enforce high test-coverage standards and outputs XML coverage reports.
  - **Static Code Analysis**: SonarQube is integrated into the Jenkins pipeline to analyze code quality and enforce quality gates based on complexity, duplications, and the coverage reports. Flake8 is utilized for syntax/linting prior to tests.
- **Containerization (Docker)**: 
  - A multi-stage-ish slim `Dockerfile` based on `python:3.12-slim` is utilized to minimize image footprints and ensure security by running the Flask web app under a non-root user (`aceest`).
  - Upon successful CI tests, Jenkins automatically builds the Docker image and pushes it to Docker Hub, tagged uniquely with the build number and the latest tag.
  - Furthermore, automated tests execute inside the containerized environment to guarantee the application works exactly as deployed.
- **Continuous Deployment (Kubernetes)**:
  - The CI/CD extends into multiple Kubernetes clusters/deployments showcasing advanced rollout strategies like Blue-Green, Canary, Shadow, A/B Testing, and Rolling Updates. 
  - Using Minikube/Cloud clusters, deployments can automatically pull the newest verified image from Docker Hub.

## 2. Deployment Strategies and Rollbacks

To prevent downtime and ensure maximum reliability during deployments, the pipeline supports multiple advanced deployment and fallback mechanisms defined via comprehensive Kubernetes YAML configurations:

1. **Rolling Update**: The default Kubernetes strategy incrementally updates pod instances. A `maxSurge` and `maxUnavailable` of 1 guarantees that at least some portion of the application remains available at all times during the upgrade.
2. **Blue-Green Deployment**: Two separate but identical environments (Blue and Green) run concurrently. The `blue-green.yaml` routes traffic to the stable 'Blue' version while the new 'Green' version is deployed and tested. Traffic is switched instantaneously by updating the Service selector, facilitating immediate rollbacks if issues occur.
3. **Canary Release**: Evaluates a new version (Canary) with a small portion of actual traffic. As configured in `canary.yaml`, setting replica ratios (e.g., 3 stable vs. 1 canary) dynamically diverts 25% of users to test the new update. If errors are observed, the canary pods can be quickly destroyed.
4. **Shadow Deployment**: Leveraging Istio's VirtualServices (`shadow.yaml`), incoming production traffic is mirrored to the new application version. Real users are unaffected as the shadow responses are discarded, allowing stress testing on production traffic.
5. **A/B Testing**: Uses HTTP header routing (e.g., user groups) defined in Istio (`ab-testing.yaml`) to send specific target demographics (e.g., beta testers) to the experimental version to gather metrics before full deployment.

## 3. Challenges Faced and Mitigation Strategies

- **Challenge: Database State Management Across Containers**: While running tests inside ephemeral Docker containers, the SQLite database state was frequently reset, breaking stateful integration tests.
  - **Mitigation**: Configured Pytest fixtures to dynamically create isolated, in-memory databases or temporary file databases on a per-test-run basis, ensuring state isolation and consistency.

- **Challenge: Ensuring Zero Downtime During Updates**: Transitioning from a desktop Tkinter application to a Web/Containerized architecture required addressing connection drops during updates.
  - **Mitigation**: Developed advanced Kubernetes manifest files with strict Readiness and Liveness probes. The deployment strategies (Canary, Blue/Green) combined with these probes ensured traffic was never routed to an unhealthy or starting container.

- **Challenge: SonarQube Integration in Ephemeral Environments**: Gathering code coverage from a containerized process back to the Jenkins host for SonarQube analysis caused permission and path-mapping issues.
  - **Mitigation**: Reordered the pipeline to execute `pytest-cov` on the host worker during the CI stage, generate the `coverage.xml`, and directly consume it within the SonarScanner step before the final Docker build step. A supplementary containerized test phase validates the built image independently.

## 4. Key Automation Outcomes

1. **Streamlined SDLC**: By pushing code, developers inherently trigger linting, unit testing, security analysis, Docker image building, and container pushing—without any manual intervention.
2. **Increased Code Quality**: Quality gates set in SonarQube restrict poor-quality, uncovered, or vulnerable code from progressing to the build stage. 
3. **Reproducibility**: The "Works on my machine" problem was eliminated by containerizing the application and testing inside the specific container image intended for production.
4. **Resilient Deployments**: The repository now holds complete configurations for 5 major deployment strategies, granting the business the flexibility to test risky features in shadow mode or confidently execute Blue-Green deployments with a near-instant rollback buffer.

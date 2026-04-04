# 🏋️ ACEest Fitness & Gym – DevOps CI/CD Pipeline

> A Flask-based fitness and gym management web application with a fully automated CI/CD pipeline using **GitHub Actions** and **Jenkins**.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Local Setup & Execution](#local-setup--execution)
- [Running Tests Manually](#running-tests-manually)
- [Docker Usage](#docker-usage)
- [CI/CD Pipeline Overview](#cicd-pipeline-overview)
  - [GitHub Actions](#github-actions)
  - [Jenkins Integration](#jenkins-integration)
- [API Endpoints](#api-endpoints)
- [Version History](#version-history)

---

## 🎯 Project Overview

ACEest Fitness & Gym is a web application designed for managing gym clients, tracking workouts, generating AI-style training programs, monitoring membership status, and calculating BMI. The project demonstrates modern **DevOps practices** including:

- **Version Control** with Git/GitHub (descriptive commits, branch management)
- **Unit Testing** with Pytest (30+ test cases)
- **Containerization** with Docker (optimized, non-root image)
- **CI/CD Automation** with GitHub Actions & Jenkins

---

## ✨ Features

| Feature                   | Description                                                   |
| ------------------------- | ------------------------------------------------------------- |
| **Client Management**     | Full CRUD operations for gym clients                          |
| **Workout Tracking**      | Log and retrieve workout sessions per client                  |
| **AI Program Generator**  | Generate workout plans based on program type and experience   |
| **BMI Calculator**        | Calculate BMI and get WHO category classification             |
| **Calorie Estimator**     | Estimate daily calorie needs based on weight and program      |
| **Membership Tracking**   | Check active/expired membership status with expiry dates      |
| **Health Check Endpoint** | `/health` endpoint for container orchestration and monitoring |

---

## 🛠 Tech Stack

| Layer              | Technology            |
| ------------------ | --------------------- |
| **Backend**        | Python 3.12 + Flask   |
| **Database**       | SQLite3               |
| **Testing**        | Pytest                |
| **Linting**        | Flake8                |
| **Containerization** | Docker              |
| **CI/CD**          | GitHub Actions        |
| **Build Server**   | Jenkins               |

---

## 📁 Project Structure

```
devopsAssignment1/
├── app.py                          # Flask application (main source)
├── test_app.py                     # Pytest test suite
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker image definition
├── Jenkinsfile                     # Jenkins pipeline definition
├── .gitignore                      # Git ignore rules
├── .github/
│   └── workflows/
│       └── main.yml                # GitHub Actions CI/CD workflow
├── templates/
│   └── index.html                  # Landing page template
└── README.md                       # This file
```

---

## 🚀 Local Setup & Execution

### Prerequisites

- Python 3.10+ installed
- pip (Python package manager)
- Git
- Docker (optional, for container testing)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/saaiarjun27/devopsAssignment1.git
cd devopsAssignment1

# 2. Create a virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The application will start on **http://localhost:5000**

---

## 🧪 Running Tests Manually

```bash
# Run the full test suite with verbose output
pytest test_app.py -v

# Run with detailed failure info
pytest test_app.py -v --tb=long

# Run a specific test class
pytest test_app.py::TestBMICalculation -v

# Run with coverage (install pytest-cov first)
pip install pytest-cov
pytest test_app.py --cov=app --cov-report=term-missing
```

### Test Coverage Summary

The test suite validates:

- ✅ Health-check endpoint
- ✅ Home page rendering
- ✅ BMI calculation logic + endpoint (including edge cases)
- ✅ Calorie estimation with all program types
- ✅ AI program generation (beginner / intermediate / advanced)
- ✅ Client CRUD (create, read, update, delete)
- ✅ Workout logging & retrieval
- ✅ Membership status checking (active / expired / not found)
- ✅ Programs listing endpoint
- ✅ Error handling (missing fields, invalid data)

---

## 🐳 Docker Usage

### Build the Docker Image

```bash
docker build -t aceest-fitness:latest .
```

### Run the Container

```bash
docker run -p 5000:5000 aceest-fitness:latest
```

Visit **http://localhost:5000** in your browser.

### Run Tests Inside the Container

```bash
docker run --rm aceest-fitness:latest python -m pytest test_app.py -v
```

### Docker Image Highlights

- **Base image**: `python:3.12-slim` (minimal footprint)
- **Non-root user**: Runs as `aceest` user for security
- **Layer caching**: Dependencies installed before copying source
- **Health check**: Built-in `HEALTHCHECK` instruction

---

## ⚙️ CI/CD Pipeline Overview

### GitHub Actions

The pipeline is defined in `.github/workflows/main.yml` and is triggered on every **push** or **pull_request** to the `main` branch.

```
┌─────────────────────┐     ┌──────────────────────┐     ┌─────────────────────────┐
│  Stage 1:           │     │  Stage 2:            │     │  Stage 3:               │
│  Build & Lint       │────▶│  Docker Image        │────▶│  Automated Testing      │
│                     │     │  Assembly            │     │  (Pytest in Container)  │
│  • Install deps     │     │  • docker build      │     │  • Run test_app.py      │
│  • flake8 lint      │     │  • Verify image      │     │  • All 30+ tests        │
│  • Verify imports   │     │                      │     │                         │
└─────────────────────┘     └──────────────────────┘     └─────────────────────────┘
```

| Stage               | What It Does                                              |
| -------------------- | --------------------------------------------------------- |
| **Build & Lint**     | Installs dependencies, runs flake8 syntax/error checks    |
| **Docker Assembly**  | Builds the Docker image and verifies it was created       |
| **Automated Testing**| Runs the full Pytest suite inside the Docker container     |

### Jenkins Integration

The `Jenkinsfile` defines a **declarative pipeline** with:

1. **Checkout** – Pulls latest code from GitHub
2. **Install Dependencies** – `pip install -r requirements.txt`
3. **Lint** – Runs flake8 for syntax validation
4. **Test** – Executes Pytest suite
5. **Docker Build** – Builds and tags Docker image

#### Jenkins Setup Steps

1. Install Jenkins on your server/local machine
2. Install required plugins: **Git**, **Pipeline**, **Docker Pipeline**
3. Create a **New Pipeline** job
4. Under **Pipeline → Definition**, select **Pipeline script from SCM**
5. Set **SCM** to **Git** and enter the repository URL:
   ```
   https://github.com/saaiarjun27/devopsAssignment1.git
   ```
6. Set **Script Path** to `Jenkinsfile`
7. Save and click **Build Now**

---

## 📡 API Endpoints

| Method   | Endpoint                        | Description                     |
| -------- | ------------------------------- | ------------------------------- |
| `GET`    | `/`                             | Landing page                    |
| `GET`    | `/health`                       | Health check                    |
| `GET`    | `/api/programs`                 | List available programs         |
| `GET`    | `/api/clients`                  | List all clients                |
| `POST`   | `/api/clients`                  | Create/update a client          |
| `GET`    | `/api/clients/<name>`           | Get a specific client           |
| `DELETE` | `/api/clients/<name>`           | Delete a client                 |
| `GET`    | `/api/workouts/<client_name>`   | Get workouts for a client       |
| `POST`   | `/api/workouts`                 | Log a new workout               |
| `POST`   | `/api/bmi`                      | Calculate BMI                   |
| `POST`   | `/api/generate-program`         | Generate AI workout program     |
| `GET`    | `/api/membership/<client_name>` | Check membership status         |

---

## 📜 Version History

| Version  | Description                                                 |
| -------- | ----------------------------------------------------------- |
| `1.0`    | Initial Tkinter GUI – basic program display                 |
| `1.1`    | Added client profile inputs, calorie estimation             |
| `1.1.2`  | Multi-client support, CSV export, progress chart            |
| `2.0.1`  | SQLite database integration                                 |
| `2.1.2`  | Database schema with workouts and exercises tables          |
| `2.2.1`  | Role-based login system                                     |
| `2.2.4`  | Full dashboard with AI program generator and PDF reports    |
| `3.0.1`  | Membership management and billing                           |
| `3.1.2`  | Refactored UI with modal login and analytics tab            |
| `3.2.4`  | Streamlined codebase, workout treeview                      |
| **4.0**  | **Flask web app + Docker + CI/CD pipeline (current)**       |

---

## 👤 Author

**Sai Arjun** – Junior DevOps Engineer  
GitHub: [@saaiarjun27](https://github.com/saaiarjun27)

---

## 📄 License

This project is developed as part of a DevOps academic assignment.



# 🏋️‍♂️ ACEest Fitness & Gym Management System

[![Click to Access Application](https://img.shields.io/badge/Live%20App-Online-brightgreen?logo=render&labelColor=blue)](https://aceest-fitness-gym.onrender.com)

<!-- Badges -->
[![Latest Release](https://img.shields.io/github/v/release/IonMind/ACEest_Fitness_Py?label=Latest%20Release)](https://github.com/IonMind/ACEest_Fitness_Py/releases)
![CI/CD Status](https://github.com/IonMind/ACEest_Fitness_Py/actions/workflows/ci-cd.yml/badge.svg)
![License](https://img.shields.io/github/license/IonMind/ACEest_Fitness_Py)
![Open Issues](https://img.shields.io/github/issues/IonMind/ACEest_Fitness_Py)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Open Pull Requests](https://img.shields.io/github/issues-pr/IonMind/ACEest_Fitness_Py)

A modern Flask web application for tracking workouts, workout time, and calories burned. Designed for fitness enthusiasts and gym managers to easily log and visualize workout data. Includes automated testing and CI/CD pipeline with GitHub Actions.

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [🛠️ Setup & Run Locally](#️-setup--run-locally)
- [🧪 Running Tests](#-running-tests)
- [🐳 Docker Usage](#-docker-usage)
- [🔄 GitHub Actions CI/CD](#-github-actions-cicd)
- [📂 Project Structure](#-project-structure)
- [🧰 Technologies Used](#-technologies-used)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features
- 📝 Add workouts: Log workout name, duration (minutes), and calories burned.
- 📋 View workouts: See a list of all logged workouts in a clean, modern interface.
- 📱 Responsive web UI: Simple, beautiful HTML & CSS for desktop and mobile.
- 🐳 Dockerized: Ready to deploy anywhere with Docker.
- ✅ Automated testing and CI/CD pipeline.

---

## 🛠️ Setup & Run Locally

1. **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/ACEest_Fitness_Py.git
    cd ACEest_Fitness_Py
    ```
2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3. **Run the Application**
    ```bash
    python src/app.py
    ```
    🌐 Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🧪 Running Tests

1. **Install Pytest** (if not already installed)
    ```bash
    pip install pytest
    ```
2. **Run Tests**
    ```bash
    pytest
    ```
    🟢 Test results will be displayed in the terminal.

---

## 🐳 Docker Usage

1. **Build the Application Image**
    ```bash
    docker build -t aceest-fitness .
    ```
2. **Run the Application Container**
    ```bash
    docker run -p 5000:5000 aceest-fitness
    ```
3. **Build the Test Image**
    ```bash
    docker build -f testdockerfile -t aceest-fitness-test .
    ```
4. **Run Tests in Docker**
    ```bash
    docker run --rm aceest-fitness-test
    ```
    📄 The test report (`report.xml`) will be generated inside the container at `/gym/report.xml`.

---

## 🔄 GitHub Actions CI/CD

This repository includes a fully automated CI/CD pipeline using GitHub Actions:
- 🚦 **Triggers:** On every push to any branch and on pull requests to `main`.
- 🏗️ **Builds:** Docker images for both the application and tests.
- 🧪 **Testing:** Executes Pytest unit tests inside the test Docker image.
- 📦 **Artifacts:** Persists and uploads the Pytest report (`report.xml`) for review.

See the workflow file at `.github/workflows/ci-cd.yml` for details.

---

## 📂 Project Structure
```
ACEest_Fitness_Py/
├── dockerfile
├── testdockerfile
├── requirements.txt
├── src/
│   └── app.py
├── tests/
│   └── test_app.py
└── .github/
    └── workflows/
        └── ci-cd.yml
```

---

## 🧰 Technologies Used
- 🐍 Python 3.11+
- ⚡ Flask
- 🎨 HTML & CSS
- 🐳 Docker
- 🧪 Pytest
- 🤖 GitHub Actions

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License
This project is licensed under the MIT License.

---

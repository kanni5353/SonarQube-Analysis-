# Advanced CI/CD Pipeline for Python with SonarQube, MongoDB, and AI Analysis

This repository contains a declarative `Jenkinsfile` for orchestrating a complete CI/CD workflow. The pipeline is designed to automate the testing, analysis, and reporting for Python-based projects, integrating powerful tools like SonarQube for static analysis, MongoDB for data persistence, and the Gemini API for generating AI-powered code improvement suggestions.

## ✨ Features

* **Automated CI/CD:** A fully automated, multi-stage pipeline managed by Jenkins.
* **Python Environment Setup:** Automatically creates a virtual environment and installs all necessary project dependencies from a `requirements.txt` file.
* **Testing & Code Coverage:** Dynamically discovers and runs unit tests, generating a code coverage report for SonarQube.
* **SonarQube Static Analysis:** Performs in-depth code quality and security analysis to identify bugs, vulnerabilities, and code smells.
* **MongoDB Integration:** Fetches the detailed analysis report from the SonarQube API and stores the metrics in a MongoDB database for historical tracking and further analysis.
* **AI-Powered Suggestions:** Leverages the Gemini API to analyze the SonarQube findings and generate intelligent, actionable suggestions for code improvement.
* **Automated Email Reporting:** Generates a clean HTML report summarizing the analysis and sends it to stakeholders, attaching an Excel file with the AI suggestions.

## ⚙️ Workflow Overview

The pipeline executes a sequence of automated tasks to provide a comprehensive overview of the project's health:

`[GitHub Repo] ➔ [Jenkins CI] ➔ [Unit Tests & Coverage] ➔ [SonarQube Analysis] ➔ [Sync to MongoDB] ➔ [Generate AI Suggestions] ➔ [Email Report]`

## 🔧 Configuration & Setup

To use this pipeline, you must configure several external services and update the placeholder values within the `Jenkinsfile`.

### ⚠️ **Important:** Update These Hardcoded Values

The following variables and paths are hardcoded in the `Jenkinsfile`. You **must** replace them with your own configuration before running the pipeline.

| Variable / Location | Placeholder Value in `Jenkinsfile` | Description / Your Value |
| :--- | :--- | :--- |
| **SonarQube Host** | `http://Your_Sonar_Host_URL` | The URL of your SonarQube server. |
| **SonarQube Token**| `credentials('sonarqube')` | The ID of your SonarQube token stored in Jenkins Credentials. |
| **MongoDB Host** | `http://Your_MongoDB_Host_URL` | The connection URI for your MongoDB instance. |
| **MongoDB Database**| `new_ai_code_suggestions` | The name of the MongoDB database you want to use. |
| **Results Collection**| `ML_analysis_results` | The MongoDB collection for storing the raw SonarQube metrics. |
| **Suggestions Collection**| `AI_Suggestions` | The MongoDB collection for storing the AI-generated suggestions. |
| **Sonar Scanner Path**| `/opt/sonar-scanner/bin` | The absolute path to the Sonar Scanner executable on your Jenkins agent. |
| **Gemini API Key**| `credentials('gemini_key')` | The ID of your Google AI (Gemini) API key stored in Jenkins Credentials. |
| **Git Repository** | `https://github.com/kanni5353/Malicious-URL-Classification.git` | In the 'Checkout Code' stage, change this to the URL of the repository you want to analyze. |
| **Email Recipient** | `kanishka2k15@gmail.com` | In the 'Send Email' stage, change this to your desired recipient's email address. |
| **Helper Scripts Path**| `/home/ubuntu/` | The pipeline expects the Python helper scripts (`sync_to_mongo.py`, `final_ai.py`, `generate_email_body.py`) to be in this directory on the Jenkins agent. |

## 🐍 Python Dependencies (`requirements.txt`)

Your target Python project should contain a `requirements.txt` file listing its dependencies. The pipeline's own helper scripts rely on the following key libraries, which should also be included:

```
# Example requirements.txt
pandas
pymongo
requests
google-generativeai
coverage
# ... add other libraries your project needs
```

## 🚀 How to Use

1.  **Prerequisites:**
    * A running Jenkins server with the **Email Extension (emailext)** and **Credentials** plugins installed.
    * A running SonarQube server.
    * A running MongoDB instance accessible from your Jenkins agent.
    * Python 3 and `venv` installed on the Jenkins agent.
    * The Sonar Scanner installed on the Jenkins agent (e.g., at `/opt/sonar-scanner`).

2.  **Setup Jenkins Credentials:**
    * In Jenkins, go to `Manage Jenkins` -> `Credentials`.
    * Store your SonarQube token as a "Secret text" credential. Note its **ID** (e.g., `sonarqube`).
    * Store your Gemini API key as another "Secret text" credential. Note its **ID** (e.g., `gemini_key`).

3.  **Place Helper Scripts:**
    * Ensure the Python helper scripts (`sync_to_mongo.py`, `final_ai.py`, `generate_email_body.py`) are placed on the Jenkins agent in the specified directory (e.g., `/home/ubuntu/`).

4.  **Configure the Pipeline Job:**
    * Create a new **Pipeline** job in Jenkins.
    * In the "Pipeline" section, select "Pipeline script" and paste the entire content of this `Jenkinsfile`.
    * **Carefully review and update** all the placeholder values in the `environment` block and other stages as detailed in the configuration table above.

5.  **Run the Build:**
    * Save the pipeline configuration.
    * Click "Build Now" to start the pipeline. It will execute all the stages and send an email report upon successful completion.

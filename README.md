# Conspector Software Composition Analyzer

## Features

Conspector Software Composition Analyzer is a tool for managing and analyzing software dependencies, identifying vulnerabilities, and providing security insights based on the latest commit in a GitHub repository. It performs the following tasks:

- **SBOM Generation**: Generates a Software Bill of Materials (SBOM) for a given GitHub repository.
- **Vulnerability Scanning**: Scans the SBOM for known vulnerabilities using Grype and provides a detailed report.
- **Exploit Detection**: Checks for the presence of known exploits associated with CVEs.
- **Export**: Exports vulnerability data to a JSON file and allows exporting to other formats such as Excel.

---

## Setup Instructions

### 1. Setting up Prerequisites in `requirements.txt`

Create and install the required Python dependencies using `requirements.txt`. This file contains all the necessary packages for the tool to run:

pip install -r requirements.txt

### 2. Setting up Syft
Syft is a tool that generates a Software Bill of Materials (SBOM). Install it to generate SBOMs from GitHub repositories.

To install Syft:

Download the latest version following the instructions on the Syft GitHub page:
https://github.com/anchore/syft/

Verify the installation:

syft --version

### 3. Setting up Grype
Grype is used to scan the SBOM for vulnerabilities. You need to install Grype:

Download the latest version from the Grype GitHub page:

https://github.com/anchore/grype

Verify the installation:

grype --version

### How to Use the Tool

### 1. Set up Variables in .env
Before running the Flask app, ensure that you have configured the following environment variables in your .env file:

GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_github_owner
GITHUB_REPO=your_github_repo
GITHUB_BRANCH=your_github_branch (optional, default is master)
REPORT_OUTPUT_DIR=/path/to/report/directory
Replace the values with your actual GitHub information and directory paths.

### 2. Running the Flask App
The Flask app exposes an endpoint /process-latest that processes the latest commit from your GitHub repository, generates the SBOM, and scans for vulnerabilities.

### 3. Triggering the Flask App Endpoint

Using Terminal (Linux/macOS):
To trigger the process_latest_commit endpoint, use curl:

curl -X GET http://127.0.0.1:5000/process-latest

Using PowerShell (Windows):
To trigger the process_latest_commit endpoint, use Invoke-RestMethod:

Invoke-RestMethod -Uri "http://127.0.0.1:5000/process-latest" -Method Get

### Conclusion
This tool helps streamline the process of analyzing and securing software components by providing detailed insights into dependencies and vulnerabilities. Follow the setup instructions carefully to get started, and use the Flask endpoint to trigger the SBOM generation and vulnerability scanning process.

For more details, refer to the official documentation of Syft and Grype.
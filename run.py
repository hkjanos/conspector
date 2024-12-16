import os
import logging
from app.utils.github import fetch_latest_commit
from app.sbom.generator import generate_sbom
from app.vulnerability.vuln_scanner import scan_vulnerabilities  # Import the vulnerability scanner
from app.utils.config import load_env
from flask import Flask, jsonify, current_app as app

# Load environment variables from .env
load_env()  # Ensure environment variables are loaded from .env

# Initialize Flask app
app = Flask(__name__)

# Setting up logging for debug mode
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Load GitHub-related variables from environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")  # GitHub repository owner
GITHUB_REPO = os.getenv("GITHUB_REPO")    # GitHub repository name
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "master")  # Default to 'master' branch

# Ensure that essential environment variables are set
if not all([GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO]):
    raise ValueError("GitHub environment variables (GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO) must be set in .env")

# API route to process the latest commit and generate the SBOM
@app.route('/process-latest', methods=['GET'])
def process_latest_commit():
    try:
        # Fetch the latest commit details by passing the necessary arguments
        response = fetch_latest_commit(GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH)

        # Check if fetch_latest_commit returned an error
        if isinstance(response, tuple):
            error_data, status_code = response
            return jsonify(error_data), status_code

        # Print the raw response to check its content
        app.logger.debug(f"GitHub API response: {response}")

        # Ensure response is valid and contains JSON data
        if isinstance(response, dict) and 'commit' in response:
            commit_data = response['commit']
            commit_sha = commit_data["sha"]
            branch = response["name"]
            repo_url = response["_links"]["html"]

            app.logger.info(f"Processing branch {branch} with commit {commit_sha} from {repo_url}")

            # Step 1: Generate SBOM
            sbom_file_path = generate_sbom(repo_url, branch)

            if not sbom_file_path:
                return jsonify({
                    "msg": "Failed to generate SBOM",
                    "commit": commit_sha,
                    "repo_url": repo_url
                }), 500

            # Step 2: Scan vulnerabilities in the SBOM
            vulnerabilities_report = scan_vulnerabilities(sbom_file_path)

            if not vulnerabilities_report:
                return jsonify({
                    "msg": "Failed to scan SBOM for vulnerabilities",
                    "commit": commit_sha,
                    "repo_url": repo_url,
                    "sbom_path": sbom_file_path
                }), 500
            else:
                app.logger.info(f"Latest commit is processed: \r\n"
                                f"SBOM FILE and Vulnerability report can be found: {os.path.dirname(sbom_file_path)}")

            # Step 3: Return the response with both SBOM path and vulnerabilities report path
            return jsonify({
                "msg": "Successfully processed latest commit, generated SBOM, and completed vulnerability scan",
                "branch": branch,
                "commit": commit_sha,
                "repo_url": repo_url,
                "sbom_path": sbom_file_path,
                "vulnerabilities_report": vulnerabilities_report  # Path to vulnerabilities report
            })
        else:
            app.logger.error(f"GitHub API returned unexpected response: {response}")
            return jsonify({"error": "Unexpected GitHub response", "details": str(response)}), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e), "msg": "Failed to process the latest commit"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

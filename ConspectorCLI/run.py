import os
import logging
from flask import Flask, jsonify, request, render_template
from app.utils.github import fetch_latest_commit
from app.sbom.generator import generate_sbom
from app.vulnerability.vuln_scanner import scan_vulnerabilities
from app.utils.config import load_env, save_env
from io import StringIO

# Load environment variables from .env
load_env()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session management

# Setting up logging for debug mode
log_buffer = StringIO()  # Buffer to store logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

# Custom log handler to write logs to the buffer
class BufferingHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        log_buffer.seek(0, 2)  # Move to the end of the buffer
        log_buffer.write(self.format(record) + "\n")

# Add the custom handler to the logger
log_handler = BufferingHandler()
log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(log_handler)
app.logger.addHandler(log_handler)


@app.route('/')
def home():
    """Render the home page where users can interact with the tool."""
    env_variables = {
        "GITHUB_SECRET": os.getenv("GITHUB_SECRET", ""),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", ""),
        "GITHUB_OWNER": os.getenv("GITHUB_OWNER", ""),
        "GITHUB_REPO": os.getenv("GITHUB_REPO", ""),
        "GITHUB_BRANCH": os.getenv("GITHUB_BRANCH", ""),
        "SBOM_TOOL_PATH": os.getenv("SBOM_TOOL_PATH", ""),
        "GRYPE_TOOL_PATH": os.getenv("GRYPE_TOOL_PATH", ""),
        "REPORT_OUTPUT_DIR": os.getenv("REPORT_OUTPUT_DIR", ""),
    }
    return render_template('index.html', env_variables=env_variables)


@app.route('/update-env', methods=['POST'])
def update_env():
    """Update .env file with new environment variables."""
    try:
        new_env = request.json
        save_env(new_env)
        app.logger.info("Environment variables updated.")
        return jsonify({"status": "success", "message": "Environment variables updated."})
        load_env() # updating environmental variables in the system.
    except Exception as e:
        app.logger.error(f"Error updating environment variables: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/get-logs', methods=['GET'])
def get_logs():
    """Serve the logs as plain text."""
    log_buffer.seek(0)  # Move to the beginning of the buffer
    logs = log_buffer.read()
    return logs, 200, {'Content-Type': 'text/plain'}


@app.route('/process-latest', methods=['GET'])
def process_latest_commit_ui():
    """Handle the request to process the latest commit and scan vulnerabilities."""
    try:
        app.logger.info("Processing the latest commit...")
        GITHUB_OWNER = os.getenv("GITHUB_OWNER")
        GITHUB_REPO = os.getenv("GITHUB_REPO")
        GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "master")

        response = fetch_latest_commit(GITHUB_OWNER, GITHUB_REPO, GITHUB_BRANCH)

        if isinstance(response, tuple):
            error_data, status_code = response
            app.logger.error(f"Error fetching the latest commit: {error_data}")
            return jsonify(error_data), status_code

        if isinstance(response, dict) and 'commit' in response:
            commit_data = response['commit']
            commit_sha = commit_data["sha"]
            branch = response["name"]
            repo_url = response["_links"]["html"]

            app.logger.info(f"Latest commit fetched: {commit_sha}")

            # Step 1: Generate SBOM
            sbom_file_path = generate_sbom(repo_url, branch)
            if not sbom_file_path:
                app.logger.error("Failed to generate SBOM.")
                return jsonify({"msg": "Failed to generate SBOM", "commit": commit_sha, "repo_url": repo_url}), 500

            app.logger.info("SBOM generated successfully.")

            # Step 2: Scan vulnerabilities in the SBOM
            vulnerabilities_report = scan_vulnerabilities(sbom_file_path)

            if not vulnerabilities_report:
                app.logger.error("Failed to scan SBOM for vulnerabilities.")
                return jsonify({
                    "msg": "Failed to scan SBOM for vulnerabilities",
                    "commit": commit_sha,
                    "repo_url": repo_url,
                    "sbom_path": sbom_file_path
                }), 500
            else:
                app.logger.info("Vulnerability scan completed successfully.")
                return jsonify({
                    "msg": "Successfully processed latest commit and scanned for vulnerabilities",
                    "commit": commit_sha,
                    "repo_url": repo_url,
                    "sbom_path": sbom_file_path,
                    "vulnerabilities_report": vulnerabilities_report  # Path to vulnerabilities report
                })
        else:
            app.logger.error("Unexpected GitHub response.")
            return jsonify({"error": "Unexpected GitHub response", "details": str(response)}), 500

    except Exception as e:
        app.logger.error(f"Error processing latest commit: {e}")
        return jsonify({"error": str(e), "msg": "Failed to process the latest commit"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

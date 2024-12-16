import hmac
import hashlib
import os
from flask import Flask, request, jsonify
from app.utils.github import fetch_latest_commit
from app.sbom.generator import generate_sbom
from app.utils.config import load_env
from app.utils.logger import setup_logging

load_env()
setup_logging()

app = Flask(__name__)
GITHUB_SECRET = os.getenv("GITHUB_SECRET")

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events."""
    if 'X-Hub-Signature-256' not in request.headers:
        return "Forbidden: Missing signature header.", 403

    signature = request.headers['X-Hub-Signature-256']
    payload = request.data
    computed_hmac = 'sha256=' + hmac.new(GITHUB_SECRET.encode(), payload, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hmac, signature):
        return "Forbidden: Signature mismatch.", 403

    event = request.headers.get('X-GitHub-Event', 'ping')
    payload_json = request.json

    if event == 'ping':
        return jsonify({'msg': 'pong'})

    if event == 'push':
        repo_name = payload_json['repository']['full_name']
        branch = payload_json['ref']
        commit_id = payload_json['head_commit']['id']
        app.logger.info(f"Received push event: {repo_name}, branch: {branch}, commit: {commit_id}")
        sbom_result = generate_sbom(repo_name, branch)
        return jsonify(sbom_result)

    return "Event not handled", 400

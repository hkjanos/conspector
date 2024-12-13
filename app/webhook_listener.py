import os
import hmac
import hashlib
from flask import Flask, request, jsonify
from app.utils.config import load_env

# Load environment variables
load_env()  # Ensure environment variables are loaded from .env

app = Flask(__name__)

# Read the GitHub secret from the environment variables
GITHUB_SECRET = os.getenv('GITHUB_SECRET')
if not GITHUB_SECRET:
    raise ValueError("GITHUB_SECRET environment variable is not set.")

@app.route('/webhook', methods=['POST'])
def github_webhook():
    # Verify the payload using the secret
    if 'X-Hub-Signature-256' not in request.headers:
        return "Forbidden: Missing signature header.", 403

    signature = request.headers['X-Hub-Signature-256']
    payload = request.data
    computed_hmac = 'sha256=' + hmac.new(GITHUB_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    print(f"Computed HMAC: {computed_hmac}")

    if not hmac.compare_digest(computed_hmac, signature):
        print(f"Received HMAC: {signature}")
        print(f"Payload received: {payload}")
        return "Forbidden: Signature mismatch.", 403

    # Parse the payload
    event = request.headers.get('X-GitHub-Event', 'ping')
    payload_json = request.json

    if event == 'ping':
        return jsonify({'msg': 'pong'})

    elif event == 'push':
        repo_name = payload_json['repository']['full_name']
        branch = payload_json['ref']
        commit_id = payload_json['head_commit']['id']
        print(f"Received push event for repo: {repo_name}, branch: {branch}, commit: {commit_id}")
        # Add custom logic here
        return jsonify({'msg': f'Received push event for {repo_name}.'})

    return "Event not handled", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

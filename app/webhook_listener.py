import os
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.json
    event = request.headers.get('X-GitHub-Event')

    if event == 'push':
        repo_name = payload['repository']['full_name']
        branch = payload['ref']
        print(f"Received push event for repo: {repo_name}, branch: {branch}")

        # Trigger SBOM generation here after push
        generate_sbom(repo_name)

        return jsonify({'msg': f'Generated SBOM for {repo_name}.'})

    return "Event not handled", 400

def generate_sbom(repo_name):
    # Change this to your project directory if necessary
    project_dir = '/path/to/your/project'

    print(f"Generating SBOM for {repo_name}...")
    result = subprocess.run(
        ['syft', 'dir:' + project_dir, '--output', 'spdx-json', '--file', f'{repo_name}-sbom.json'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Error generating SBOM: {result.stderr}")
    else:
        print(f"SBOM for {repo_name} generated successfully: {result.stdout}")
        # Optionally, you can upload or store this SBOM file in your project
        save_sbom(f'{repo_name}-sbom.json')

def save_sbom(filename):
    # Example: Saving the SBOM file locally or uploading it somewhere
    print(f"Saving SBOM to {filename}...")
    with open(f'/path/to/save/{filename}', 'w') as f:
        f.write(filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

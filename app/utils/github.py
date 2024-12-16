import requests
import os

def fetch_latest_commit(github_owner, github_repo, github_branch):
    """Fetch the latest commit details from the specified GitHub repo and branch."""
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable is not set.")

    url = f"https://api.github.com/repos/{github_owner}/{github_repo}/branches/{github_branch}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Will raise an HTTPError for bad responses

        return response.json()

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching latest commit details: {str(e)}")

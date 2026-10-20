"""
github.py

Retrieves recent commits and their code changes from a real GitHub repository
using the GitHub API.

The commit information is later used by Gemini to identify which code
changes might have caused a production incident.
"""
import os
import requests


def recent_commits(owner, repo, limit=8, branch=None):
    """
    Retrieves recent commits and modified files from a GitHub repository.

    Connects to the GitHub API to fetch recent commits, then retrieves
    details about each commit, including its message, timestamp, and
    modified code. This information is used to investigate possible
    causes of an incident.

    Args:
        owner (str): GitHub username or organization that owns the repository.
        repo (str): Name of the GitHub repository.
        limit (int): Maximum number of commits to retrieve (default is 8).
        branch (str or None): Branch to retrieve commits from. If None,
                              GitHub uses the repository's default branch.

    Returns:
        list: A list of dictionaries containing each commit's SHA,
              message, date, and modified files with their code patches.
    """

    # Headers specify the GitHub API response format and identify our application.
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "incident-response-demo"}

    # Uses a GitHub token if available for authentication.
    # Public repositories can also be accessed without a token.
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"

    # Constructs the GitHub API URL for the specified repository.
    base = f"https://api.github.com/repos/{owner}/{repo}"

    # Limits the number of commits returned by GitHub.
    params = {"per_page": limit}

    # If a branch is provided, retrieves commits from that branch.
    if branch:
        params["sha"] = branch

    # Sends an HTTP GET request to retrieve recent commits.
    response = requests.get(f"{base}/commits", headers=headers, params=params, timeout=15)
    # Raises an error if the API request fails (e.g., 404 or 403).
    response.raise_for_status()
    commits = []

    # Loops through each commit returned by the GitHub API.
    for item in response.json():
        # SHA is the unique identifier of the commit.
        sha = item["sha"]
        # Makes another API request to retrieve detailed information
        # about this commit, including the modified files and code changes.
        detail = requests.get(f"{base}/commits/{sha}", headers=headers, timeout=15)

        detail.raise_for_status()
        # Retrieves up to 12 modified files from the commit.
        # get("files", []) returns an empty list if the field is missing.
        files = detail.json().get("files", [])[:12]

        # Stores the relevant information about the commit.
        commits.append({
            "sha": sha,

            # Keeps only the first line of the commit message.
            "message": item["commit"]["message"].splitlines()[0],
            "date": item["commit"]["committer"]["date"],

            # Creates a simplified list of modified files.
            # Each file includes its name, change status, and code patch.
             # get("patch", "") handles files without a patch.
                    # [:1200] limits the patch to its first 1200 characters.
            "files": [{"name": f["filename"], "status": f["status"],
                       "patch": f.get("patch", "")[:1200]} for f in files],
        })

    # Returns all retrieved commits to the investigation pipeline.
    return commits

"""
doomsday-network/github-bounty-scanner
Patch for: https://github.com/doomsday-network/github-bounty-scanner/issues/1

Implements: scan_bounties.py
- Scans starred repositories for bounties.
- Mines 1 pool share if all 4 Doomsday repos are starred.
- Clean, modular, production-ready, pure Python.
- No external dependencies.

Assumptions:
- User's starred repos are fetched via GitHub API (token required).
- Bounty issues are labeled with 'bounty'.
- Mining a pool share is simulated (no real blockchain interaction).
- The 4 Doomsday repos are known and hardcoded.

Author: OpenAI Assistant
"""

import json
from typing import List, Dict, Optional, Any

# Constants
DOOMSDAY_REPOS = [
    "doomsday-network/doomsday-contracts",
    "doomsday-network/doomsday-app",
    "doomsday-network/doomsday-bounties",
    "doomsday-network/github-bounty-scanner"
]

GITHUB_API_URL = "https://api.github.com"

def get_github_headers(token: str) -> Dict[str, str]:
    """
    Returns headers for GitHub API requests.
    """
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def github_api_request(url: str, headers: Dict[str, str]) -> Optional[Any]:
    """
    Makes a GET request to the GitHub API and returns the parsed JSON response.
    Pure Python implementation using urllib.
    """
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError

    req = Request(url, headers=headers)
    try:
        with urlopen(req) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            data = resp.read().decode(charset)
            return json.loads(data)
    except (HTTPError, URLError) as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_starred_repos(token: str) -> List[str]:
    """
    Returns a list of 'owner/repo' strings the user has starred.
    Handles pagination.
    """
    headers = get_github_headers(token)
    starred = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/user/starred?per_page=100&page={page}"
        data = github_api_request(url, headers)
        if not data:
            break
        for repo in data:
            full_name = repo.get("full_name")
            if full_name:
                starred.append(full_name)
        if len(data) < 100:
            break
        page += 1
    return starred

def has_starred_all_doomsday_repos(starred: List[str]) -> bool:
    """
    Returns True if all Doomsday repos are starred.
    """
    return all(repo in starred for repo in DOOMSDAY_REPOS)

def get_bounty_issues(repo: str, token: str) -> List[Dict[str, Any]]:
    """
    Returns a list of open issues labeled 'bounty' for the given repo.
    """
    headers = get_github_headers(token)
    issues = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/repos/{repo}/issues?state=open&labels=bounty&per_page=100&page={page}"
        data = github_api_request(url, headers)
        if not data:
            break
        for issue in data:
            # Exclude pull requests
            if "pull_request" not in issue:
                issues.append(issue)
        if len(data) < 100:
            break
        page += 1
    return issues

def scan_bounties(token: str) -> List[Dict[str, Any]]:
    """
    Scans all starred repos for open bounty issues.
    Returns a list of bounty issue dicts.
    """
    starred = get_starred_repos(token)
    bounties = []
    for repo in starred:
        issues = get_bounty_issues(repo, token)
        for issue in issues:
            bounties.append({
                "repo": repo,
                "issue_number": issue.get("number"),
                "title": issue.get("title"),
                "url": issue.get("html_url"),
                "labels": [l.get("name") for l in issue.get("labels", [])]
            })
    return bounties

def mine_pool_share(token: str) -> bool:
    """
    Simulates mining 1 pool share.
    In production, this would interact with the Doomsday network.
    Here, we just print a message and return True.
    """
    print("🎉 Mined 1 pool share for starring all Doomsday repos!")
    return True

def main() -> None:
    """
    Main entry point.
    """
    import os

    print("=== Doomsday Network GitHub Bounty Scanner ===")
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: Please set your GitHub personal access token in the GITHUB_TOKEN environment variable.")
        return

    starred = get_starred_repos(token)
    print(f"Starred repos found: {len(starred)}")

    if has_starred_all_doomsday_repos(starred):
        print("✅ You have starred all 4 Doomsday repos!")
        mine_pool_share(token)
    else:
        missing = [r for r in DOOMSDAY_REPOS if r not in starred]
        print("❌ You have NOT starred all Doomsday repos.")
        print("Missing:", ", ".join(missing))

    print("Scanning for bounty issues in your starred repos...")
    bounties = scan_bounties(token)
    if bounties:
        print(f"Found {len(bounties)} bounty issues:")
        for b in bounties:
            print(f"- [{b['repo']}] #{b['issue_number']}: {b['title']} ({b['url']})")
    else:
        print("No bounty issues found in your starred repos.")

if __name__ == "__main__":
    main()
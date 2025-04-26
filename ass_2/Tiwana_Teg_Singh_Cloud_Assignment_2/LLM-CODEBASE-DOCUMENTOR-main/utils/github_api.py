import requests
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class RepoMetadata:
    """Class to store GitHub repository metadata."""
    
    def __init__(self, data: Dict[str, Any]):
        self.name = data.get('name', '')
        self.full_name = data.get('full_name', '')
        self.description = data.get('description', 'No description available')
        self.url = data.get('html_url', '')
        self.api_url = data.get('url', '')
        self.stars = data.get('stargazers_count', 0)
        self.forks = data.get('forks_count', 0)
        self.issues = data.get('open_issues_count', 0)
        self.language = data.get('language', 'Unknown')
        self.updated_at = data.get('updated_at', '')
        self.readme_summary = None  # To be filled in later

    def __str__(self):
        return f"{self.full_name} ({self.stars}⭐, {self.language})"

def github_search_repos(
    keywords: List[str], 
    filter_params: Optional[Dict[str, Any]] = None, 
    token: Optional[str] = None
) -> List[RepoMetadata]:
    """
    Search GitHub repositories using the GitHub Search API.
    
    Args:
        keywords: List of keywords to search for
        filter_params: Dictionary with filtering parameters 
            (min_stars, min_forks, language, sort_by, updated_since)
        token: GitHub API token for authenticated requests
    
    Returns:
        List of RepoMetadata objects
    """
    # Default headers
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Add authorization if token provided
    if token:
        headers['Authorization'] = f'token {token}'
    
    # Build query string
    query = ' '.join(keywords)
    
    # Apply filters if provided
    if filter_params:
        if filter_params.get('min_stars'):
            query += f" stars:>={filter_params['min_stars']}"
        
        if filter_params.get('min_forks'):
            query += f" forks:>={filter_params['min_forks']}"
        
        if filter_params.get('language'):
            query += f" language:{filter_params['language']}"
        
        if filter_params.get('updated_since'):
            # Convert to ISO format for GitHub API
            query += f" pushed:>{filter_params['updated_since']}"
    
    # Set up parameters for the search request
    params = {
        'q': query,
        'sort': filter_params.get('sort_by', 'stars'),
        'order': 'desc',
        'per_page': 10  # Limit to 10 results
    }
    
    url = 'https://api.github.com/search/repositories'
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        repos = [RepoMetadata(item) for item in data.get('items', [])]
        
        return repos
    except requests.RequestException as e:
        print(f"GitHub API error: {e}")
        return []

def get_readme_content(repo_full_name: str, token: Optional[str] = None) -> str:
    """
    Fetch README content for a GitHub repository.
    
    Args:
        repo_full_name: Full name of the repository (owner/repo)
        token: GitHub API token for authenticated requests
    
    Returns:
        README content as string or error message
    """
    # Default headers
    headers = {
        'Accept': 'application/vnd.github.v3.raw'
    }
    
    # Add authorization if token provided
    if token:
        headers['Authorization'] = f'token {token}'
    
    url = f'https://api.github.com/repos/{repo_full_name}/readme'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.text
    except requests.RequestException as e:
        return f"Error fetching README: {e}"

if __name__ == "__main__":
    # Test the GitHub API functions
    token = os.environ.get('GITHUB_TOKEN')
    test_keywords = ["python", "llm", "framework"]
    test_filters = {
        "min_stars": 100,
        "language": "Python",
        "sort_by": "stars"
    }
    
    print(f"Searching for: {test_keywords} with filters: {test_filters}")
    repos = github_search_repos(test_keywords, test_filters, token)
    
    for repo in repos:
        print(f"{repo.name}: {repo.stars}⭐ - {repo.description[:50]}...") 
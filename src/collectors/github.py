"""
GitHub API Data Collector
Fetches repository metrics: stars, forks, commits, issues
"""

import requests
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.config import GITHUB_TOKEN, GITHUB_DELAY, RAW_DATA_DIR
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class GitHubCollector:
    """Collects data from GitHub API for repository metrics"""

    def __init__(self, token: str = None):
        """
        Initialize GitHub collector

        Args:
            token: GitHub personal access token
        """
        self.token = token or GITHUB_TOKEN
        if not self.token:
            logger.warning("No GitHub token provided. Rate limits will be strict (60/hour).")

        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _make_request(self, url: str, params: dict = None) -> Optional[dict]:
        """
        Make request to GitHub API with error handling

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response or None if failed
        """
        try:
            time.sleep(GITHUB_DELAY)  # Rate limiting
            response = self.session.get(url, params=params)

            # Check rate limit
            remaining = response.headers.get('X-RateLimit-Remaining')
            if remaining:
                logger.debug(f"GitHub API rate limit remaining: {remaining}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.warning(f"Repository not found: {url}")
            elif response.status_code == 403:
                logger.error(f"Rate limit exceeded or forbidden: {url}")
            else:
                logger.error(f"HTTP error fetching {url}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching {url}: {e}")
            return None

    def get_repo_info(self, repo_path: str) -> Optional[Dict]:
        """
        Get basic repository information

        Args:
            repo_path: Repository path (e.g., 'owner/repo')

        Returns:
            Repository data dict or None
        """
        url = f"{self.base_url}/repos/{repo_path}"
        data = self._make_request(url)

        if not data:
            return None

        # Extract key metrics
        return {
            'name': data.get('name'),
            'full_name': data.get('full_name'),
            'description': data.get('description'),
            'stars': data.get('stargazers_count'),
            'forks': data.get('forks_count'),
            'open_issues': data.get('open_issues_count'),
            'watchers': data.get('watchers_count'),
            'size': data.get('size'),
            'language': data.get('language'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at'),
            'pushed_at': data.get('pushed_at'),
            'homepage': data.get('homepage'),
            'topics': data.get('topics', []),
        }

    def get_commit_activity(self, repo_path: str) -> Optional[Dict]:
        """
        Get commit activity statistics

        Args:
            repo_path: Repository path

        Returns:
            Commit activity data or None
        """
        url = f"{self.base_url}/repos/{repo_path}/stats/commit_activity"
        data = self._make_request(url)

        if not data:
            return None

        # Calculate total commits in last year
        total_commits = sum(week.get('total', 0) for week in data) if isinstance(data, list) else 0

        return {
            'total_commits_last_year': total_commits,
            'weekly_activity': data if isinstance(data, list) else []
        }

    def get_contributors(self, repo_path: str) -> Optional[Dict]:
        """
        Get contributor statistics

        Args:
            repo_path: Repository path

        Returns:
            Contributor data or None
        """
        url = f"{self.base_url}/repos/{repo_path}/contributors"
        params = {'per_page': 100}  # Get top 100 contributors
        data = self._make_request(url, params=params)

        if not data or not isinstance(data, list):
            return None

        return {
            'total_contributors': len(data),
            'top_contributor_commits': data[0].get('contributions', 0) if data else 0,
        }

    def collect_repo_metrics(self, repo_path: str, tech_name: str) -> Dict:
        """
        Collect all metrics for a repository

        Args:
            repo_path: Repository path
            tech_name: Technology name for logging

        Returns:
            Complete metrics dictionary
        """
        logger.info(f"Collecting GitHub data for {tech_name} ({repo_path})")

        metrics = {
            'technology': tech_name,
            'repository': repo_path,
            'collected_at': datetime.now().isoformat(),
            'source': 'github',
        }

        # Get basic info
        repo_info = self.get_repo_info(repo_path)
        if repo_info:
            metrics.update(repo_info)
        else:
            logger.warning(f"Failed to get basic info for {tech_name}")
            metrics['error'] = 'Failed to fetch repository info'
            return metrics

        # Get commit activity
        commit_activity = self.get_commit_activity(repo_path)
        if commit_activity:
            metrics['commit_activity'] = commit_activity
        else:
            logger.warning(f"Failed to get commit activity for {tech_name}")

        # Get contributors
        contributors = self.get_contributors(repo_path)
        if contributors:
            metrics['contributors'] = contributors
        else:
            logger.warning(f"Failed to get contributors for {tech_name}")

        return metrics

    def collect_for_list(self, tech_list: Dict, list_name: str) -> List[Dict]:
        """
        Collect GitHub data for all technologies in a list

        Args:
            tech_list: Technology list dictionary
            list_name: Name of the list (for file naming)

        Returns:
            List of metrics dictionaries
        """
        logger.info(f"Starting GitHub collection for {list_name}")
        all_metrics = []

        for tech in tech_list['technologies']:
            if 'github' not in tech:
                logger.info(f"Skipping {tech['name']} - no GitHub repository")
                continue

            metrics = self.collect_repo_metrics(
                repo_path=tech['github'],
                tech_name=tech['name']
            )
            all_metrics.append(metrics)

        # Save to file
        output_dir = RAW_DATA_DIR / list_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'github_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)

        logger.info(f"Saved GitHub data to {output_file}")
        logger.info(f"Collected {len(all_metrics)} repositories for {list_name}")

        return all_metrics


def collect_github_data(list_name: str = None) -> Dict[str, List[Dict]]:
    """
    Collect GitHub data for one or all strategic lists

    Args:
        list_name: Optional list name ('enterprise' or 'fintech')
                  If None, collects for all lists

    Returns:
        Dictionary mapping list names to metrics
    """
    from ..utils.config import ACTIVE_LISTS

    collector = GitHubCollector()
    results = {}

    lists_to_process = {list_name: ACTIVE_LISTS[list_name]} if list_name else ACTIVE_LISTS

    for name, tech_list in lists_to_process.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing {name.upper()} list")
        logger.info(f"{'='*60}")

        metrics = collector.collect_for_list(tech_list, name)
        results[name] = metrics

    return results


if __name__ == "__main__":
    # Test collection
    print("Testing GitHub data collection...")
    results = collect_github_data()
    print(f"\nCollected data for {len(results)} lists")
    for list_name, metrics in results.items():
        print(f"  {list_name}: {len(metrics)} repositories")

"""
PyPI Data Collector
Fetches package download statistics and metadata from Python Package Index
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import time

from ..utils.config import RAW_DATA_DIR
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class PyPICollector:
    """Collects download statistics and metadata from PyPI"""

    def __init__(self):
        """Initialize PyPI collector"""
        self.pypi_url = "https://pypi.org/pypi"
        self.pypistats_url = "https://pypistats.org/api"
        self.session = requests.Session()

    def _make_request(self, url: str, retry_count: int = 3) -> Optional[dict]:
        """
        Make request to PyPI API with error handling and retries

        Args:
            url: API endpoint URL
            retry_count: Number of retries on failure

        Returns:
            JSON response or None if failed
        """
        for attempt in range(retry_count):
            try:
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    logger.warning(f"Package not found: {url}")
                    return None
                elif response.status_code == 429:
                    # Rate limited, wait and retry
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"HTTP error fetching {url}: {e}")
                    return None

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error fetching {url}: {e}")
                if attempt < retry_count - 1:
                    time.sleep(1)
                    continue
                return None

        return None

    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """
        Get package metadata from PyPI

        Args:
            package_name: PyPI package name

        Returns:
            Package metadata or None
        """
        url = f"{self.pypi_url}/{package_name}/json"
        data = self._make_request(url)

        if not data:
            return None

        info = data.get('info', {})

        return {
            'name': info.get('name'),
            'version': info.get('version'),
            'summary': info.get('summary'),
            'description_content_type': info.get('description_content_type'),
            'author': info.get('author'),
            'license': info.get('license'),
            'home_page': info.get('home_page'),
            'project_url': info.get('project_url'),
            'requires_python': info.get('requires_python'),
            'keywords': info.get('keywords'),
            'classifiers': info.get('classifiers', []),
        }

    def get_download_stats_recent(self, package_name: str) -> Optional[Dict]:
        """
        Get recent download statistics from pypistats.org

        Args:
            package_name: PyPI package name

        Returns:
            Download statistics or None
        """
        url = f"{self.pypistats_url}/packages/{package_name}/recent"
        data = self._make_request(url)

        if not data or 'data' not in data:
            return None

        stats = data['data']

        return {
            'last_day': stats.get('last_day', 0),
            'last_week': stats.get('last_week', 0),
            'last_month': stats.get('last_month', 0),
        }

    def get_download_stats_overall(self, package_name: str) -> Optional[Dict]:
        """
        Get overall download statistics

        Args:
            package_name: PyPI package name

        Returns:
            Download statistics or None
        """
        url = f"{self.pypistats_url}/packages/{package_name}/overall"
        data = self._make_request(url)

        if not data or 'data' not in data:
            return None

        # Calculate totals from the data
        downloads_data = data.get('data', [])
        if not downloads_data:
            return None

        # Get recent data points (last 30 days)
        recent_data = downloads_data[-30:] if len(downloads_data) >= 30 else downloads_data
        total_recent = sum(item.get('downloads', 0) for item in recent_data)

        return {
            'total_downloads_30_day': total_recent,
            'average_daily': total_recent / len(recent_data) if recent_data else 0,
            'data_points': len(downloads_data),
        }

    def collect_package_metrics(self, package_name: str, tech_name: str) -> Dict:
        """
        Collect all metrics for a PyPI package

        Args:
            package_name: PyPI package name
            tech_name: Technology name for logging

        Returns:
            Complete metrics dictionary
        """
        logger.info(f"Collecting PyPI data for {tech_name} ({package_name})")

        metrics = {
            'technology': tech_name,
            'package': package_name,
            'collected_at': datetime.now().isoformat(),
            'source': 'pypi',
        }

        # Get package info
        package_info = self.get_package_info(package_name)
        if package_info:
            metrics.update(package_info)
        else:
            logger.warning(f"Failed to get package info for {tech_name}")
            metrics['error'] = 'Package not found or API error'
            return metrics

        # Get recent download stats
        recent_stats = self.get_download_stats_recent(package_name)
        if recent_stats:
            metrics['downloads_recent'] = recent_stats
        else:
            logger.warning(f"Failed to get recent download stats for {tech_name}")

        # Get overall download stats
        overall_stats = self.get_download_stats_overall(package_name)
        if overall_stats:
            metrics['downloads_overall'] = overall_stats
        else:
            logger.warning(f"Failed to get overall download stats for {tech_name}")

        # Small delay to be respectful to API
        time.sleep(0.5)

        return metrics

    def collect_for_list(self, tech_list: Dict, list_name: str) -> List[Dict]:
        """
        Collect PyPI data for all technologies in a list

        Args:
            tech_list: Technology list dictionary
            list_name: Name of the list (for file naming)

        Returns:
            List of metrics dictionaries
        """
        logger.info(f"Starting PyPI collection for {list_name}")
        all_metrics = []

        for tech in tech_list['technologies']:
            if 'pypi' not in tech:
                logger.info(f"Skipping {tech['name']} - no PyPI package")
                continue

            metrics = self.collect_package_metrics(
                package_name=tech['pypi'],
                tech_name=tech['name']
            )
            all_metrics.append(metrics)

        # Save to file
        output_dir = RAW_DATA_DIR / list_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'pypi_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)

        logger.info(f"Saved PyPI data to {output_file}")
        logger.info(f"Collected {len(all_metrics)} packages for {list_name}")

        return all_metrics


def collect_pypi_data(list_name: str = None) -> Dict[str, List[Dict]]:
    """
    Collect PyPI data for one or all strategic lists

    Args:
        list_name: Optional list name ('enterprise' or 'fintech')
                  If None, collects for all lists

    Returns:
        Dictionary mapping list names to metrics
    """
    from ..utils.config import ACTIVE_LISTS

    collector = PyPICollector()
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
    print("Testing PyPI data collection...")
    results = collect_pypi_data()
    print(f"\nCollected data for {len(results)} lists")
    for list_name, metrics in results.items():
        print(f"  {list_name}: {len(metrics)} packages")

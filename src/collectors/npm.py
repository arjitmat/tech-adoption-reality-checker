"""
npm API Data Collector
Fetches package download statistics from npm registry
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.config import RAW_DATA_DIR
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class NpmCollector:
    """Collects download statistics from npm registry"""

    def __init__(self):
        """Initialize npm collector"""
        self.registry_url = "https://registry.npmjs.org"
        self.downloads_url = "https://api.npmjs.org/downloads"
        self.session = requests.Session()

    def _make_request(self, url: str) -> Optional[dict]:
        """
        Make request to npm API with error handling

        Args:
            url: API endpoint URL

        Returns:
            JSON response or None if failed
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                logger.warning(f"Package not found: {url}")
            else:
                logger.error(f"HTTP error fetching {url}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching {url}: {e}")
            return None

    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """
        Get package metadata from npm registry

        Args:
            package_name: npm package name

        Returns:
            Package metadata or None
        """
        url = f"{self.registry_url}/{package_name}"
        data = self._make_request(url)

        if not data:
            return None

        # Get latest version info
        latest_version = data.get('dist-tags', {}).get('latest', 'unknown')
        version_info = data.get('versions', {}).get(latest_version, {})

        return {
            'name': data.get('name'),
            'description': data.get('description'),
            'latest_version': latest_version,
            'license': version_info.get('license'),
            'homepage': data.get('homepage'),
            'repository': data.get('repository', {}).get('url'),
            'keywords': data.get('keywords', []),
            'created': data.get('time', {}).get('created'),
            'modified': data.get('time', {}).get('modified'),
        }

    def get_download_stats(self, package_name: str, period: str = 'last-month') -> Optional[Dict]:
        """
        Get download statistics for a package

        Args:
            package_name: npm package name
            period: Time period ('last-day', 'last-week', 'last-month', 'last-year')

        Returns:
            Download statistics or None
        """
        url = f"{self.downloads_url}/point/{period}/{package_name}"
        data = self._make_request(url)

        if not data:
            return None

        return {
            'downloads': data.get('downloads', 0),
            'start': data.get('start'),
            'end': data.get('end'),
            'period': period
        }

    def get_download_range(self, package_name: str, days: int = 30) -> Optional[Dict]:
        """
        Get download statistics for a date range

        Args:
            package_name: npm package name
            days: Number of days to look back

        Returns:
            Download statistics or None
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        url = f"{self.downloads_url}/range/{start_str}:{end_str}/{package_name}"
        data = self._make_request(url)

        if not data:
            return None

        downloads = data.get('downloads', [])
        total = sum(day.get('downloads', 0) for day in downloads)

        return {
            'total_downloads': total,
            'start_date': start_str,
            'end_date': end_str,
            'days': days,
            'daily_average': total / days if days > 0 else 0,
            'daily_data': downloads
        }

    def collect_package_metrics(self, package_name: str, tech_name: str) -> Dict:
        """
        Collect all metrics for an npm package

        Args:
            package_name: npm package name
            tech_name: Technology name for logging

        Returns:
            Complete metrics dictionary
        """
        logger.info(f"Collecting npm data for {tech_name} ({package_name})")

        metrics = {
            'technology': tech_name,
            'package': package_name,
            'collected_at': datetime.now().isoformat(),
            'source': 'npm',
        }

        # Get package info
        package_info = self.get_package_info(package_name)
        if package_info:
            metrics.update(package_info)
        else:
            logger.warning(f"Failed to get package info for {tech_name}")
            metrics['error'] = 'Package not found or API error'
            return metrics

        # Get download stats for different periods
        for period in ['last-week', 'last-month']:
            stats = self.get_download_stats(package_name, period)
            if stats:
                metrics[f'downloads_{period.replace("-", "_")}'] = stats['downloads']

        # Get detailed 30-day range
        range_stats = self.get_download_range(package_name, days=30)
        if range_stats:
            metrics['downloads_30_day'] = range_stats

        return metrics

    def collect_for_list(self, tech_list: Dict, list_name: str) -> List[Dict]:
        """
        Collect npm data for all technologies in a list

        Args:
            tech_list: Technology list dictionary
            list_name: Name of the list (for file naming)

        Returns:
            List of metrics dictionaries
        """
        logger.info(f"Starting npm collection for {list_name}")
        all_metrics = []

        for tech in tech_list['technologies']:
            if 'npm' not in tech:
                logger.info(f"Skipping {tech['name']} - no npm package")
                continue

            metrics = self.collect_package_metrics(
                package_name=tech['npm'],
                tech_name=tech['name']
            )
            all_metrics.append(metrics)

        # Save to file
        output_dir = RAW_DATA_DIR / list_name
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'npm_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)

        logger.info(f"Saved npm data to {output_file}")
        logger.info(f"Collected {len(all_metrics)} packages for {list_name}")

        return all_metrics


def collect_npm_data(list_name: str = None) -> Dict[str, List[Dict]]:
    """
    Collect npm data for one or all strategic lists

    Args:
        list_name: Optional list name ('enterprise' or 'fintech')
                  If None, collects for all lists

    Returns:
        Dictionary mapping list names to metrics
    """
    from ..utils.config import ACTIVE_LISTS

    collector = NpmCollector()
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
    print("Testing npm data collection...")
    results = collect_npm_data()
    print(f"\nCollected data for {len(results)} lists")
    for list_name, metrics in results.items():
        print(f"  {list_name}: {len(metrics)} packages")

"""
Main data collection script
Orchestrates collection from all sources (GitHub, npm, PyPI)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.github import collect_github_data
from src.collectors.npm import collect_npm_data
from src.collectors.pypi import collect_pypi_data
from src.utils.logger import get_default_logger

logger = get_default_logger(__name__)


def collect_all_data(list_name: str = None):
    """
    Collect data from all sources

    Args:
        list_name: Optional list name to collect for ('enterprise' or 'fintech')
                  If None, collects for all lists
    """
    logger.info("="*70)
    logger.info("TECH ADOPTION DATA COLLECTION - STARTING")
    logger.info("="*70)

    if list_name:
        logger.info(f"Collecting data for: {list_name.upper()} list only")
    else:
        logger.info("Collecting data for: ALL lists (Enterprise AI + Fintech AI)")

    # Collect from GitHub
    try:
        logger.info("\n" + "="*70)
        logger.info("PHASE 1: GitHub Data Collection")
        logger.info("="*70)
        github_results = collect_github_data(list_name)
        logger.info(f"✓ GitHub collection completed")
    except Exception as e:
        logger.error(f"✗ GitHub collection failed: {e}")
        github_results = {}

    # Collect from npm
    try:
        logger.info("\n" + "="*70)
        logger.info("PHASE 2: npm Data Collection")
        logger.info("="*70)
        npm_results = collect_npm_data(list_name)
        logger.info(f"✓ npm collection completed")
    except Exception as e:
        logger.error(f"✗ npm collection failed: {e}")
        npm_results = {}

    # Collect from PyPI
    try:
        logger.info("\n" + "="*70)
        logger.info("PHASE 3: PyPI Data Collection")
        logger.info("="*70)
        pypi_results = collect_pypi_data(list_name)
        logger.info(f"✓ PyPI collection completed")
    except Exception as e:
        logger.error(f"✗ PyPI collection failed: {e}")
        pypi_results = {}

    # Summary
    logger.info("\n" + "="*70)
    logger.info("DATA COLLECTION SUMMARY")
    logger.info("="*70)

    all_lists = set(list(github_results.keys()) + list(npm_results.keys()) + list(pypi_results.keys()))

    for lst in all_lists:
        logger.info(f"\n{lst.upper()} List:")
        logger.info(f"  GitHub: {len(github_results.get(lst, []))} repositories")
        logger.info(f"  npm:    {len(npm_results.get(lst, []))} packages")
        logger.info(f"  PyPI:   {len(pypi_results.get(lst, []))} packages")

    logger.info("\n" + "="*70)
    logger.info("✓ ALL DATA COLLECTION COMPLETED")
    logger.info("="*70)

    return {
        'github': github_results,
        'npm': npm_results,
        'pypi': pypi_results
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Collect technology adoption data')
    parser.add_argument(
        '--list',
        choices=['enterprise', 'fintech'],
        help='Specific list to collect (default: all lists)'
    )

    args = parser.parse_args()

    collect_all_data(list_name=args.list)

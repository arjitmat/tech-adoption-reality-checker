"""
Data Quality Checker
Cross-validates signals across multiple sources to detect hype vs real adoption
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..utils.config import RAW_DATA_DIR, MIN_SOURCES_FOR_HIGH_CONFIDENCE, DIVERGENCE_THRESHOLD
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class DataQualityChecker:
    """Validates data quality through multi-source cross-validation"""

    def __init__(self):
        """Initialize quality checker"""
        self.raw_data_dir = RAW_DATA_DIR

    def load_latest_data(self, list_name: str, source: str) -> Optional[List[Dict]]:
        """
        Load the most recent data file for a source

        Args:
            list_name: Name of the list (enterprise/fintech)
            source: Data source (github/npm/pypi)

        Returns:
            List of data dictionaries or None
        """
        data_dir = self.raw_data_dir / list_name
        if not data_dir.exists():
            logger.warning(f"Data directory not found: {data_dir}")
            return None

        # Find latest file for this source
        pattern = f"{source}_*.json"
        files = sorted(data_dir.glob(pattern), reverse=True)

        if not files:
            logger.warning(f"No {source} data found for {list_name}")
            return None

        latest_file = files[0]
        logger.info(f"Loading {source} data from {latest_file.name}")

        try:
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {latest_file}: {e}")
            return None

    def normalize_technology_name(self, name: str) -> str:
        """
        Normalize technology names for comparison across sources

        Args:
            name: Technology name

        Returns:
            Normalized name
        """
        return name.lower().replace('-', '').replace('_', '').strip()

    def extract_metrics(self, data: Dict, source: str) -> Dict:
        """
        Extract key metrics from source data

        Args:
            data: Data dictionary from a source
            source: Source name (github/npm/pypi)

        Returns:
            Normalized metrics dictionary
        """
        metrics = {
            'source': source,
            'technology': data.get('technology'),
            'collected_at': data.get('collected_at'),
        }

        if source == 'github':
            metrics.update({
                'stars': data.get('stars', 0),
                'forks': data.get('forks', 0),
                'open_issues': data.get('open_issues', 0),
                'watchers': data.get('watchers', 0),
                'contributors': data.get('contributors', {}).get('total_contributors', 0),
                'commits_last_year': data.get('commit_activity', {}).get('total_commits_last_year', 0),
            })

        elif source == 'npm':
            if 'error' not in data:
                metrics.update({
                    'downloads_last_week': data.get('downloads_last_week', 0),
                    'downloads_last_month': data.get('downloads_last_month', 0),
                    'downloads_30_day_total': data.get('downloads_30_day', {}).get('total_downloads', 0),
                    'downloads_30_day_avg': data.get('downloads_30_day', {}).get('daily_average', 0),
                })

        elif source == 'pypi':
            if 'error' not in data:
                recent = data.get('downloads_recent', {})
                overall = data.get('downloads_overall', {})
                metrics.update({
                    'downloads_last_day': recent.get('last_day', 0),
                    'downloads_last_week': recent.get('last_week', 0),
                    'downloads_last_month': recent.get('last_month', 0),
                    'downloads_30_day_total': overall.get('total_downloads_30_day', 0),
                    'downloads_30_day_avg': overall.get('average_daily', 0),
                })

        return metrics

    def merge_sources(self, list_name: str) -> Dict[str, Dict]:
        """
        Merge data from all sources for each technology

        Args:
            list_name: Name of the list

        Returns:
            Dictionary mapping technology names to merged metrics
        """
        logger.info(f"Merging data sources for {list_name}")

        # Load data from all sources
        github_data = self.load_latest_data(list_name, 'github') or []
        npm_data = self.load_latest_data(list_name, 'npm') or []
        pypi_data = self.load_latest_data(list_name, 'pypi') or []

        # Build merged dictionary
        merged = {}

        # Process GitHub data
        for item in github_data:
            tech_name = item.get('technology')
            if tech_name:
                normalized = self.normalize_technology_name(tech_name)
                if normalized not in merged:
                    merged[normalized] = {'technology': tech_name, 'sources': {}}
                merged[normalized]['sources']['github'] = self.extract_metrics(item, 'github')

        # Process npm data
        for item in npm_data:
            tech_name = item.get('technology')
            if tech_name:
                normalized = self.normalize_technology_name(tech_name)
                if normalized not in merged:
                    merged[normalized] = {'technology': tech_name, 'sources': {}}
                merged[normalized]['sources']['npm'] = self.extract_metrics(item, 'npm')

        # Process PyPI data
        for item in pypi_data:
            tech_name = item.get('technology')
            if tech_name:
                normalized = self.normalize_technology_name(tech_name)
                if normalized not in merged:
                    merged[normalized] = {'technology': tech_name, 'sources': {}}
                merged[normalized]['sources']['pypi'] = self.extract_metrics(item, 'pypi')

        logger.info(f"Merged data for {len(merged)} technologies")
        return merged

    def calculate_confidence_score(self, sources: Dict) -> Tuple[str, int, List[str]]:
        """
        Calculate confidence score based on source agreement

        Args:
            sources: Dictionary of source data

        Returns:
            Tuple of (confidence_level, score, available_sources)
        """
        available_sources = list(sources.keys())
        source_count = len(available_sources)

        if source_count >= MIN_SOURCES_FOR_HIGH_CONFIDENCE:
            confidence = "HIGH"
            score = 5
        elif source_count == 2:
            confidence = "MEDIUM"
            score = 3
        elif source_count == 1:
            confidence = "LOW"
            score = 1
        else:
            confidence = "NONE"
            score = 0

        return confidence, score, available_sources

    def detect_hype_signals(self, sources: Dict) -> Tuple[bool, List[str]]:
        """
        Detect potential hype by comparing signals across sources

        Args:
            sources: Dictionary of source data

        Returns:
            Tuple of (is_hype, reasons)
        """
        hype_flags = []

        # Compare GitHub stars vs package downloads
        github = sources.get('github', {})
        npm = sources.get('npm', {})
        pypi = sources.get('pypi', {})

        stars = github.get('stars', 0)

        # Check npm divergence
        if npm and 'downloads_last_month' in npm:
            npm_downloads = npm['downloads_last_month']
            # Very high stars but low downloads could indicate hype
            if stars > 10000 and npm_downloads < 1000:
                hype_flags.append("High GitHub stars but low npm downloads")

        # Check PyPI divergence
        if pypi and 'downloads_last_month' in pypi:
            pypi_downloads = pypi['downloads_last_month']
            if stars > 10000 and pypi_downloads < 10000:
                hype_flags.append("High GitHub stars but low PyPI downloads")

        # Check for extreme ratios
        if npm and pypi:
            npm_monthly = npm.get('downloads_last_month', 0)
            pypi_monthly = pypi.get('downloads_last_month', 0)

            if npm_monthly > 0 and pypi_monthly > 0:
                ratio = max(npm_monthly, pypi_monthly) / min(npm_monthly, pypi_monthly)
                if ratio > 10:  # More than 10x difference
                    hype_flags.append(f"Large divergence between npm and PyPI downloads ({ratio:.1f}x)")

        is_hype = len(hype_flags) > 0
        return is_hype, hype_flags

    def validate_list(self, list_name: str) -> Dict:
        """
        Validate data quality for a list

        Args:
            list_name: Name of the list to validate

        Returns:
            Validation report dictionary
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Validating data quality for {list_name.upper()}")
        logger.info(f"{'='*60}")

        merged_data = self.merge_sources(list_name)

        validation_report = {
            'list_name': list_name,
            'validated_at': datetime.now().isoformat(),
            'total_technologies': len(merged_data),
            'technologies': [],
            'summary': {
                'high_confidence': 0,
                'medium_confidence': 0,
                'low_confidence': 0,
                'hype_detected': 0,
            }
        }

        for tech_key, tech_data in merged_data.items():
            tech_name = tech_data['technology']
            sources = tech_data['sources']

            # Calculate confidence
            confidence, score, available = self.calculate_confidence_score(sources)

            # Detect hype
            is_hype, hype_reasons = self.detect_hype_signals(sources)

            tech_validation = {
                'technology': tech_name,
                'confidence_level': confidence,
                'confidence_score': score,
                'available_sources': available,
                'source_count': len(available),
                'hype_detected': is_hype,
                'hype_reasons': hype_reasons,
                'metrics': sources
            }

            validation_report['technologies'].append(tech_validation)

            # Update summary
            if confidence == "HIGH":
                validation_report['summary']['high_confidence'] += 1
            elif confidence == "MEDIUM":
                validation_report['summary']['medium_confidence'] += 1
            elif confidence == "LOW":
                validation_report['summary']['low_confidence'] += 1

            if is_hype:
                validation_report['summary']['hype_detected'] += 1

            # Log findings
            logger.info(f"\n{tech_name}:")
            logger.info(f"  Confidence: {confidence} ({len(available)} sources)")
            if is_hype:
                logger.warning(f"  ⚠️  Hype detected: {', '.join(hype_reasons)}")

        return validation_report


def validate_all_lists() -> Dict[str, Dict]:
    """
    Validate data quality for all lists

    Returns:
        Dictionary mapping list names to validation reports
    """
    from ..utils.config import ACTIVE_LISTS

    checker = DataQualityChecker()
    results = {}

    for list_name in ACTIVE_LISTS.keys():
        report = checker.validate_list(list_name)
        results[list_name] = report

    # Print summary
    logger.info("\n" + "="*60)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*60)

    for list_name, report in results.items():
        summary = report['summary']
        logger.info(f"\n{list_name.upper()}:")
        logger.info(f"  Total technologies: {report['total_technologies']}")
        logger.info(f"  High confidence: {summary['high_confidence']}")
        logger.info(f"  Medium confidence: {summary['medium_confidence']}")
        logger.info(f"  Low confidence: {summary['low_confidence']}")
        logger.info(f"  Hype detected: {summary['hype_detected']}")

    return results


if __name__ == "__main__":
    print("Running data quality validation...")
    results = validate_all_lists()

    # Save results
    from ..utils.config import PROCESSED_DATA_DIR
    output_file = PROCESSED_DATA_DIR / f'quality_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nValidation results saved to {output_file}")

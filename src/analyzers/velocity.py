"""
Velocity Calculator
Calculates growth rates and momentum for technology adoption
Focus on rate of change over absolute numbers
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from ..utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, VELOCITY_SPIKE_THRESHOLD
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class VelocityCalculator:
    """Calculates adoption velocity and momentum metrics"""

    def __init__(self):
        """Initialize velocity calculator"""
        self.raw_data_dir = RAW_DATA_DIR
        self.processed_data_dir = PROCESSED_DATA_DIR

    def get_historical_files(self, list_name: str, source: str, days: int = 30) -> List[Path]:
        """
        Get historical data files for a source

        Args:
            list_name: List name
            source: Data source
            days: Look back period

        Returns:
            List of file paths, sorted by date
        """
        data_dir = self.raw_data_dir / list_name
        if not data_dir.exists():
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        files = []

        for file in data_dir.glob(f"{source}_*.json"):
            # Extract timestamp from filename
            try:
                timestamp_str = file.stem.split('_', 1)[1]
                file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                if file_date >= cutoff_date:
                    files.append(file)
            except Exception:
                continue

        return sorted(files)

    def calculate_simple_velocity(self, current: float, previous: float,
                                  time_delta_days: float = 30) -> Dict:
        """
        Calculate simple velocity metrics

        Args:
            current: Current value
            previous: Previous value
            time_delta_days: Time period in days

        Returns:
            Velocity metrics dictionary
        """
        if previous == 0:
            if current > 0:
                return {
                    'growth_rate': float('inf'),
                    'growth_percentage': float('inf'),
                    'absolute_change': current,
                    'velocity_type': 'new_emergence',
                    'is_anomaly': current > 10000  # Large sudden appearance
                }
            else:
                return {
                    'growth_rate': 0,
                    'growth_percentage': 0,
                    'absolute_change': 0,
                    'velocity_type': 'no_activity',
                    'is_anomaly': False
                }

        absolute_change = current - previous
        growth_rate = absolute_change / previous
        growth_percentage = growth_rate * 100

        # Normalize to monthly rate
        monthly_factor = 30 / time_delta_days
        monthly_growth_rate = growth_rate * monthly_factor
        monthly_growth_percentage = monthly_growth_rate * 100

        # Detect anomalies
        is_anomaly = abs(monthly_growth_rate) > VELOCITY_SPIKE_THRESHOLD

        # Classify velocity
        if monthly_growth_percentage > 50:
            velocity_type = 'accelerating'
        elif monthly_growth_percentage > 10:
            velocity_type = 'growing'
        elif monthly_growth_percentage > -10:
            velocity_type = 'stable'
        elif monthly_growth_percentage > -50:
            velocity_type = 'declining'
        else:
            velocity_type = 'collapsing'

        return {
            'growth_rate': monthly_growth_rate,
            'growth_percentage': monthly_growth_percentage,
            'absolute_change': absolute_change,
            'velocity_type': velocity_type,
            'is_anomaly': is_anomaly,
            'time_delta_days': time_delta_days
        }

    def calculate_github_velocity(self, tech_name: str, list_name: str) -> Dict:
        """
        Calculate velocity metrics for GitHub data

        Args:
            tech_name: Technology name
            list_name: List name

        Returns:
            GitHub velocity metrics
        """
        files = self.get_historical_files(list_name, 'github')

        if len(files) < 2:
            logger.warning(f"Need at least 2 data points for velocity calculation for {tech_name}")
            return {'error': 'insufficient_data'}

        # Load most recent and oldest files
        latest_file = files[-1]
        oldest_file = files[0]

        try:
            with open(latest_file, 'r') as f:
                latest_data = json.load(f)
            with open(oldest_file, 'r') as f:
                oldest_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading files: {e}")
            return {'error': 'file_load_error'}

        # Find technology in both datasets
        latest_tech = next((t for t in latest_data if t.get('technology') == tech_name), None)
        oldest_tech = next((t for t in oldest_data if t.get('technology') == tech_name), None)

        if not latest_tech or not oldest_tech:
            return {'error': 'technology_not_found'}

        # Calculate time delta
        latest_time = datetime.fromisoformat(latest_tech['collected_at'])
        oldest_time = datetime.fromisoformat(oldest_tech['collected_at'])
        time_delta_days = (latest_time - oldest_time).total_seconds() / 86400

        if time_delta_days < 1:
            return {'error': 'insufficient_time_delta'}

        # Calculate velocities for each metric
        metrics = {}

        for key in ['stars', 'forks', 'watchers', 'open_issues']:
            current = latest_tech.get(key, 0)
            previous = oldest_tech.get(key, 0)
            metrics[f'{key}_velocity'] = self.calculate_simple_velocity(
                current, previous, time_delta_days
            )

        # Overall GitHub momentum score (weighted average)
        stars_weight = 0.5
        forks_weight = 0.3
        watchers_weight = 0.2

        stars_growth = metrics.get('stars_velocity', {}).get('growth_percentage', 0)
        forks_growth = metrics.get('forks_velocity', {}).get('growth_percentage', 0)
        watchers_growth = metrics.get('watchers_velocity', {}).get('growth_percentage', 0)

        # Handle infinity
        if stars_growth == float('inf'):
            stars_growth = 100
        if forks_growth == float('inf'):
            forks_growth = 100
        if watchers_growth == float('inf'):
            watchers_growth = 100

        momentum_score = (
            stars_growth * stars_weight +
            forks_growth * forks_weight +
            watchers_growth * watchers_weight
        )

        return {
            'source': 'github',
            'metrics': metrics,
            'momentum_score': momentum_score,
            'time_period_days': time_delta_days,
            'latest_values': {
                'stars': latest_tech.get('stars', 0),
                'forks': latest_tech.get('forks', 0),
                'watchers': latest_tech.get('watchers', 0),
            }
        }

    def calculate_downloads_velocity(self, tech_name: str, list_name: str, source: str) -> Dict:
        """
        Calculate velocity for download metrics (npm/pypi)

        Args:
            tech_name: Technology name
            list_name: List name
            source: 'npm' or 'pypi'

        Returns:
            Download velocity metrics
        """
        files = self.get_historical_files(list_name, source)

        if len(files) < 2:
            return {'error': 'insufficient_data'}

        latest_file = files[-1]
        oldest_file = files[0]

        try:
            with open(latest_file, 'r') as f:
                latest_data = json.load(f)
            with open(oldest_file, 'r') as f:
                oldest_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading {source} files: {e}")
            return {'error': 'file_load_error'}

        latest_tech = next((t for t in latest_data if t.get('technology') == tech_name), None)
        oldest_tech = next((t for t in oldest_data if t.get('technology') == tech_name), None)

        if not latest_tech or not oldest_tech:
            return {'error': 'technology_not_found'}

        # Check for errors in data
        if 'error' in latest_tech or 'error' in oldest_tech:
            return {'error': 'data_collection_error'}

        # Calculate time delta
        latest_time = datetime.fromisoformat(latest_tech['collected_at'])
        oldest_time = datetime.fromisoformat(oldest_tech['collected_at'])
        time_delta_days = (latest_time - oldest_time).total_seconds() / 86400

        if time_delta_days < 1:
            return {'error': 'insufficient_time_delta'}

        # Get download metrics based on source
        if source == 'npm':
            current_monthly = latest_tech.get('downloads_last_month', 0)
            previous_monthly = oldest_tech.get('downloads_last_month', 0)
        else:  # pypi
            current_monthly = latest_tech.get('downloads_recent', {}).get('last_month', 0)
            previous_monthly = oldest_tech.get('downloads_recent', {}).get('last_month', 0)

        velocity = self.calculate_simple_velocity(current_monthly, previous_monthly, time_delta_days)

        return {
            'source': source,
            'monthly_downloads_velocity': velocity,
            'time_period_days': time_delta_days,
            'latest_monthly_downloads': current_monthly,
            'previous_monthly_downloads': previous_monthly
        }

    def calculate_list_velocities(self, list_name: str) -> Dict:
        """
        Calculate velocities for all technologies in a list

        Args:
            list_name: List name

        Returns:
            Velocity report
        """
        from ..utils.config import ACTIVE_LISTS

        logger.info(f"\n{'='*60}")
        logger.info(f"Calculating velocities for {list_name.upper()}")
        logger.info(f"{'='*60}")

        tech_list = ACTIVE_LISTS[list_name]
        velocities = []

        for tech in tech_list['technologies']:
            tech_name = tech['name']
            logger.info(f"\nAnalyzing {tech_name}...")

            tech_velocity = {
                'technology': tech_name,
                'category': tech.get('category', 'unknown'),
                'calculated_at': datetime.now().isoformat(),
            }

            # GitHub velocity
            if 'github' in tech:
                github_vel = self.calculate_github_velocity(tech_name, list_name)
                tech_velocity['github'] = github_vel
                if 'error' not in github_vel:
                    logger.info(f"  GitHub momentum: {github_vel.get('momentum_score', 0):.1f}%")

            # npm velocity
            if 'npm' in tech:
                npm_vel = self.calculate_downloads_velocity(tech_name, list_name, 'npm')
                tech_velocity['npm'] = npm_vel

            # PyPI velocity
            if 'pypi' in tech:
                pypi_vel = self.calculate_downloads_velocity(tech_name, list_name, 'pypi')
                tech_velocity['pypi'] = pypi_vel

            velocities.append(tech_velocity)

        report = {
            'list_name': list_name,
            'calculated_at': datetime.now().isoformat(),
            'total_technologies': len(velocities),
            'velocities': velocities
        }

        return report


def calculate_all_velocities() -> Dict[str, Dict]:
    """
    Calculate velocities for all lists

    Returns:
        Dictionary mapping list names to velocity reports
    """
    from ..utils.config import ACTIVE_LISTS

    calculator = VelocityCalculator()
    results = {}

    for list_name in ACTIVE_LISTS.keys():
        report = calculator.calculate_list_velocities(list_name)
        results[list_name] = report

        # Save individual report
        output_file = PROCESSED_DATA_DIR / f'velocity_{list_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\nSaved velocity report to {output_file}")

    return results


if __name__ == "__main__":
    print("Calculating technology adoption velocities...")
    results = calculate_all_velocities()
    print("\n✓ Velocity calculation complete")

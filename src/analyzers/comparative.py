"""
Comparative Analyzer
Generates cross-list insights - the key differentiator
Detects patterns between enterprise AI and fintech AI adoption
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict
import statistics

from ..utils.config import PROCESSED_DATA_DIR, ACTIVE_LISTS
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class ComparativeAnalyzer:
    """Analyzes patterns across multiple strategic lists"""

    def __init__(self):
        """Initialize comparative analyzer"""
        self.processed_dir = PROCESSED_DATA_DIR

    def load_insights(self, list_name: str) -> Optional[Dict]:
        """Load latest insights for a list"""
        pattern = f"insights_{list_name}_*.json"
        files = sorted(self.processed_dir.glob(pattern), reverse=True)

        if not files:
            logger.warning(f"No insights found for {list_name}")
            return None

        with open(files[0], 'r') as f:
            return json.load(f)

    def load_velocity(self, list_name: str) -> Optional[Dict]:
        """Load latest velocity data for a list"""
        pattern = f"velocity_{list_name}_*.json"
        files = sorted(self.processed_dir.glob(pattern), reverse=True)

        if not files:
            logger.warning(f"No velocity data found for {list_name}")
            return None

        with open(files[0], 'r') as f:
            return json.load(f)

    def compare_adoption_velocity(self, list1_data: Dict, list2_data: Dict,
                                  list1_name: str, list2_name: str) -> Dict:
        """
        Compare adoption velocities between two lists

        Returns:
            Comparative velocity analysis
        """
        list1_vel = list1_data.get('velocities', [])
        list2_vel = list2_data.get('velocities', [])

        # Extract momentum scores
        list1_momenta = []
        list2_momenta = []

        for tech in list1_vel:
            github = tech.get('github', {})
            if 'error' not in github and 'momentum_score' in github:
                list1_momenta.append(github['momentum_score'])

        for tech in list2_vel:
            github = tech.get('github', {})
            if 'error' not in github and 'momentum_score' in github:
                list2_momenta.append(github['momentum_score'])

        if not list1_momenta or not list2_momenta:
            return {'error': 'insufficient_data'}

        # Calculate statistics
        list1_avg = statistics.mean(list1_momenta)
        list2_avg = statistics.mean(list2_momenta)
        list1_median = statistics.median(list1_momenta)
        list2_median = statistics.median(list2_momenta)

        velocity_diff = list1_avg - list2_avg
        velocity_ratio = list1_avg / list2_avg if list2_avg != 0 else float('inf')

        # Determine which is leading
        if abs(velocity_diff) < 5:  # Within 5% is essentially same
            leader = "tied"
            interpretation = f"{list1_name} and {list2_name} show similar adoption velocities"
        elif velocity_diff > 0:
            leader = list1_name
            interpretation = f"{list1_name} adoption is {velocity_diff:.1f}% faster than {list2_name}"
        else:
            leader = list2_name
            interpretation = f"{list2_name} adoption is {abs(velocity_diff):.1f}% faster than {list1_name}"

        return {
            f'{list1_name}_average_momentum': list1_avg,
            f'{list2_name}_average_momentum': list2_avg,
            f'{list1_name}_median_momentum': list1_median,
            f'{list2_name}_median_momentum': list2_median,
            'velocity_difference_percentage': velocity_diff,
            'velocity_ratio': velocity_ratio,
            'leader': leader,
            'interpretation': interpretation,
        }

    def identify_category_patterns(self, list1_insights: Dict, list2_insights: Dict,
                                   list1_name: str, list2_name: str) -> Dict:
        """
        Identify patterns in category adoption across lists

        Returns:
            Category pattern analysis
        """
        list1_categories = list1_insights.get('category_trends', {})
        list2_categories = list2_insights.get('category_trends', {})

        patterns = {
            'category_comparison': [],
            'unique_to_list1': [],
            'unique_to_list2': [],
            'shared_categories': []
        }

        all_categories = set(list1_categories.keys()) | set(list2_categories.keys())

        for category in all_categories:
            cat1 = list1_categories.get(category)
            cat2 = list2_categories.get(category)

            if cat1 and cat2:
                # Shared category
                patterns['shared_categories'].append(category)
                patterns['category_comparison'].append({
                    'category': category,
                    f'{list1_name}_momentum': cat1['average_momentum'],
                    f'{list2_name}_momentum': cat2['average_momentum'],
                    'momentum_gap': cat1['average_momentum'] - cat2['average_momentum'],
                    f'{list1_name}_count': cat1['technology_count'],
                    f'{list2_name}_count': cat2['technology_count']
                })
            elif cat1:
                patterns['unique_to_list1'].append({
                    'category': category,
                    'momentum': cat1['average_momentum'],
                    'tech_count': cat1['technology_count']
                })
            elif cat2:
                patterns['unique_to_list2'].append({
                    'category': category,
                    'momentum': cat2['average_momentum'],
                    'tech_count': cat2['technology_count']
                })

        return patterns

    def detect_leading_indicators(self, list1_data: Dict, list2_data: Dict,
                                  list1_name: str, list2_name: str) -> List[Dict]:
        """
        Detect potential leading indicators (technology X predicts technology Y)

        Returns:
            List of leading indicator patterns
        """
        # This is a simplified version - in reality would need historical data
        # to prove correlation, but we can identify candidates based on categories

        indicators = []

        list1_vel = list1_data.get('velocities', [])
        list2_vel = list2_data.get('velocities', [])

        # Group by category
        list1_by_cat = defaultdict(list)
        list2_by_cat = defaultdict(list)

        for tech in list1_vel:
            github = tech.get('github', {})
            if 'error' not in github and 'momentum_score' in github:
                cat = tech.get('category', 'unknown')
                list1_by_cat[cat].append({
                    'tech': tech['technology'],
                    'momentum': github['momentum_score']
                })

        for tech in list2_vel:
            github = tech.get('github', {})
            if 'error' not in github and 'momentum_score' in github:
                cat = tech.get('category', 'unknown')
                list2_by_cat[cat].append({
                    'tech': tech['technology'],
                    'momentum': github['momentum_score']
                })

        # Look for infrastructure preceding applications
        infra_categories = ['vector_db', 'ai_infrastructure', 'ml_platform']
        app_categories = ['ai_platform', 'fintech_infrastructure', 'trading_platform']

        for infra_cat in infra_categories:
            if infra_cat in list1_by_cat:
                infra_momentum = statistics.mean([t['momentum'] for t in list1_by_cat[infra_cat]])

                # Check if high infrastructure adoption precedes application adoption
                for app_cat in app_categories:
                    if app_cat in list2_by_cat:
                        app_momentum = statistics.mean([t['momentum'] for t in list2_by_cat[app_cat]])

                        if infra_momentum > app_momentum + 20:  # Infrastructure significantly ahead
                            indicators.append({
                                'indicator_type': 'infrastructure_leads_application',
                                'leading_category': infra_cat,
                                'following_category': app_cat,
                                'momentum_gap': infra_momentum - app_momentum,
                                'hypothesis': f"{infra_cat} adoption in {list1_name} may predict {app_cat} growth in {list2_name}",
                                'confidence': 'medium'  # Would need time-series data to confirm
                            })

        return indicators

    def identify_adoption_lag(self, list1_insights: Dict, list2_insights: Dict,
                             list1_name: str, list2_name: str) -> Dict:
        """
        Attempt to quantify adoption lag between markets
        Note: Limited accuracy with single snapshot, but can identify patterns

        Returns:
            Adoption lag analysis
        """
        # Compare maturity based on various signals
        list1_leaders = list1_insights.get('adoption_leaders', [])
        list2_leaders = list2_insights.get('adoption_leaders', [])

        list1_emerging = len(list1_insights.get('emerging_technologies', []))
        list2_emerging = len(list2_insights.get('emerging_technologies', []))

        # Average momentum as proxy for market maturity
        list1_avg_momentum = statistics.mean([l['momentum_score'] for l in list1_leaders]) if list1_leaders else 0
        list2_avg_momentum = statistics.mean([l['momentum_score'] for l in list2_leaders]) if list2_leaders else 0

        lag_analysis = {
            f'{list1_name}_maturity_score': list1_avg_momentum,
            f'{list2_name}_maturity_score': list2_avg_momentum,
            f'{list1_name}_emerging_count': list1_emerging,
            f'{list2_name}_emerging_count': list2_emerging,
        }

        # Interpret maturity difference
        maturity_gap = list1_avg_momentum - list2_avg_momentum

        if abs(maturity_gap) < 10:
            lag_analysis['interpretation'] = f"{list1_name} and {list2_name} markets show similar maturity"
            lag_analysis['estimated_lag'] = "minimal"
        elif maturity_gap > 0:
            lag_analysis['interpretation'] = f"{list1_name} appears more mature than {list2_name}"
            lag_analysis['estimated_lag'] = f"{list2_name} likely lags {list1_name}"
            lag_analysis['lag_magnitude'] = "significant" if maturity_gap > 30 else "moderate"
        else:
            lag_analysis['interpretation'] = f"{list2_name} appears more mature than {list1_name}"
            lag_analysis['estimated_lag'] = f"{list1_name} likely lags {list2_name}"
            lag_analysis['lag_magnitude'] = "significant" if abs(maturity_gap) > 30 else "moderate"

        # Note limitation
        lag_analysis['note'] = "Quantifying exact lag requires time-series data. Current analysis based on relative maturity signals."

        return lag_analysis

    def generate_strategic_insights(self, comparative_data: Dict) -> List[str]:
        """
        Generate strategic insight statements from comparative data

        Returns:
            List of insight strings
        """
        insights = []

        # Velocity comparison insight
        velocity = comparative_data.get('velocity_comparison', {})
        if velocity and 'interpretation' in velocity:
            insights.append(velocity['interpretation'])

        # Category patterns
        category_patterns = comparative_data.get('category_patterns', {})
        if category_patterns:
            unique1 = category_patterns.get('unique_to_list1', [])
            unique2 = category_patterns.get('unique_to_list2', [])

            if unique1:
                list1_name = comparative_data.get('lists_compared', ['list1', 'list2'])[0]
                cats = [u['category'] for u in unique1[:3]]
                insights.append(f"{list1_name} focuses uniquely on: {', '.join(cats)}")

            if unique2:
                list2_name = comparative_data.get('lists_compared', ['list1', 'list2'])[1]
                cats = [u['category'] for u in unique2[:3]]
                insights.append(f"{list2_name} focuses uniquely on: {', '.join(cats)}")

        # Leading indicators
        indicators = comparative_data.get('leading_indicators', [])
        if indicators:
            for indicator in indicators[:2]:  # Top 2
                insights.append(indicator['hypothesis'])

        # Adoption lag
        lag = comparative_data.get('adoption_lag', {})
        if lag and 'interpretation' in lag:
            insights.append(lag['interpretation'])

        return insights

    def compare_lists(self, list1_name: str, list2_name: str) -> Dict:
        """
        Comprehensive comparison between two lists

        Args:
            list1_name: First list name
            list2_name: Second list name

        Returns:
            Comparative analysis report
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"COMPARATIVE ANALYSIS: {list1_name.upper()} vs {list2_name.upper()}")
        logger.info(f"{'='*70}")

        # Load data
        list1_insights = self.load_insights(list1_name)
        list2_insights = self.load_insights(list2_name)
        list1_velocity = self.load_velocity(list1_name)
        list2_velocity = self.load_velocity(list2_name)

        if not all([list1_insights, list2_insights, list1_velocity, list2_velocity]):
            logger.error("Missing data for comparative analysis")
            return {'error': 'insufficient_data'}

        # Perform comparisons
        comparison = {
            'generated_at': datetime.now().isoformat(),
            'lists_compared': [list1_name, list2_name],
        }

        # Velocity comparison
        logger.info("\nComparing adoption velocities...")
        velocity_comp = self.compare_adoption_velocity(
            list1_velocity, list2_velocity, list1_name, list2_name
        )
        comparison['velocity_comparison'] = velocity_comp
        if 'interpretation' in velocity_comp:
            logger.info(f"  {velocity_comp['interpretation']}")

        # Category patterns
        logger.info("\nAnalyzing category patterns...")
        category_patterns = self.identify_category_patterns(
            list1_insights, list2_insights, list1_name, list2_name
        )
        comparison['category_patterns'] = category_patterns
        logger.info(f"  Shared categories: {len(category_patterns['shared_categories'])}")
        logger.info(f"  Unique to {list1_name}: {len(category_patterns['unique_to_list1'])}")
        logger.info(f"  Unique to {list2_name}: {len(category_patterns['unique_to_list2'])}")

        # Leading indicators
        logger.info("\nIdentifying potential leading indicators...")
        indicators = self.detect_leading_indicators(
            list1_velocity, list2_velocity, list1_name, list2_name
        )
        comparison['leading_indicators'] = indicators
        if indicators:
            logger.info(f"  Found {len(indicators)} potential leading indicator patterns")
            for ind in indicators:
                logger.info(f"    - {ind['hypothesis']}")

        # Adoption lag
        logger.info("\nAnalyzing adoption lag patterns...")
        lag_analysis = self.identify_adoption_lag(
            list1_insights, list2_insights, list1_name, list2_name
        )
        comparison['adoption_lag'] = lag_analysis
        logger.info(f"  {lag_analysis['interpretation']}")

        # Generate strategic insights
        logger.info("\nGenerating strategic insights...")
        strategic_insights = self.generate_strategic_insights(comparison)
        comparison['strategic_insights'] = strategic_insights

        logger.info(f"\n{'='*70}")
        logger.info("KEY STRATEGIC INSIGHTS")
        logger.info(f"{'='*70}")
        for i, insight in enumerate(strategic_insights, 1):
            logger.info(f"{i}. {insight}")

        return comparison


def generate_comparative_analysis() -> Dict:
    """
    Generate comparative analysis between all active lists

    Returns:
        Complete comparative analysis report
    """
    analyzer = ComparativeAnalyzer()

    # Get list names
    list_names = list(ACTIVE_LISTS.keys())

    if len(list_names) < 2:
        logger.error("Need at least 2 lists for comparative analysis")
        return {'error': 'insufficient_lists'}

    # Compare enterprise vs fintech
    comparison = analyzer.compare_lists(list_names[0], list_names[1])

    # Save results
    output_file = PROCESSED_DATA_DIR / f'comparative_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    logger.info(f"\nSaved comparative analysis to {output_file}")

    return comparison


if __name__ == "__main__":
    print("Generating comparative analysis...")
    results = generate_comparative_analysis()
    print("\n✓ Comparative analysis complete")

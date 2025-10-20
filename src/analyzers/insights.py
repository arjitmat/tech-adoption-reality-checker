"""
Insight Generator
Detects patterns and generates strategic insights from quality and velocity data
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict

from ..utils.config import PROCESSED_DATA_DIR, TOP_N_INSIGHTS
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class InsightGenerator:
    """Generates strategic insights from analyzed data"""

    def __init__(self):
        """Initialize insight generator"""
        self.processed_dir = PROCESSED_DATA_DIR

    def load_quality_data(self, list_name: str) -> Dict:
        """Load latest quality validation data"""
        pattern = f"quality_validation_*.json"
        files = sorted(self.processed_dir.glob(pattern), reverse=True)

        if not files:
            logger.warning(f"No quality data found")
            return {}

        with open(files[0], 'r') as f:
            data = json.load(f)
            return data.get(list_name, {})

    def load_velocity_data(self, list_name: str) -> Dict:
        """Load latest velocity data"""
        pattern = f"velocity_{list_name}_*.json"
        files = sorted(self.processed_dir.glob(pattern), reverse=True)

        if not files:
            logger.warning(f"No velocity data found for {list_name}")
            return {}

        with open(files[0], 'r') as f:
            return json.load(f)

    def identify_adoption_leaders(self, velocity_data: Dict, n: int = 5) -> List[Dict]:
        """
        Identify technologies with highest adoption velocity

        Args:
            velocity_data: Velocity report
            n: Number of leaders to return

        Returns:
            List of leader dictionaries
        """
        velocities = velocity_data.get('velocities', [])
        leaders = []

        for tech in velocities:
            github = tech.get('github', {})
            if 'error' in github or 'momentum_score' not in github:
                continue

            momentum = github['momentum_score']
            leaders.append({
                'technology': tech['technology'],
                'category': tech.get('category', 'unknown'),
                'momentum_score': momentum,
                'github_stars': github.get('latest_values', {}).get('stars', 0),
                'velocity_type': github.get('metrics', {}).get('stars_velocity', {}).get('velocity_type', 'unknown')
            })

        # Sort by momentum score
        leaders.sort(key=lambda x: x['momentum_score'], reverse=True)
        return leaders[:n]

    def identify_hype_candidates(self, quality_data: Dict) -> List[Dict]:
        """
        Identify technologies with hype signals

        Args:
            quality_data: Quality validation report

        Returns:
            List of hype candidates
        """
        technologies = quality_data.get('technologies', [])
        hype_candidates = []

        for tech in technologies:
            if tech.get('hype_detected', False):
                hype_candidates.append({
                    'technology': tech['technology'],
                    'confidence_level': tech['confidence_level'],
                    'hype_reasons': tech['hype_reasons'],
                    'available_sources': tech['available_sources']
                })

        return hype_candidates

    def analyze_category_trends(self, velocity_data: Dict) -> Dict[str, Dict]:
        """
        Analyze trends by technology category

        Args:
            velocity_data: Velocity report

        Returns:
            Dictionary of category trends
        """
        velocities = velocity_data.get('velocities', [])
        categories = defaultdict(list)

        for tech in velocities:
            category = tech.get('category', 'unknown')
            github = tech.get('github', {})

            if 'error' not in github and 'momentum_score' in github:
                categories[category].append({
                    'technology': tech['technology'],
                    'momentum': github['momentum_score']
                })

        # Calculate category statistics
        category_trends = {}
        for category, techs in categories.items():
            if not techs:
                continue

            momenta = [t['momentum'] for t in techs]
            category_trends[category] = {
                'technology_count': len(techs),
                'average_momentum': sum(momenta) / len(momenta),
                'max_momentum': max(momenta),
                'min_momentum': min(momenta),
                'technologies': sorted(techs, key=lambda x: x['momentum'], reverse=True)
            }

        return category_trends

    def detect_emerging_technologies(self, velocity_data: Dict) -> List[Dict]:
        """
        Detect emerging technologies (new or rapidly accelerating)

        Args:
            velocity_data: Velocity report

        Returns:
            List of emerging technologies
        """
        velocities = velocity_data.get('velocities', [])
        emerging = []

        for tech in velocities:
            github = tech.get('github', {})
            if 'error' in github:
                continue

            metrics = github.get('metrics', {})
            stars_vel = metrics.get('stars_velocity', {})

            # Check for emergence or rapid growth
            if stars_vel.get('velocity_type') in ['accelerating', 'new_emergence']:
                emerging.append({
                    'technology': tech['technology'],
                    'category': tech.get('category', 'unknown'),
                    'velocity_type': stars_vel.get('velocity_type'),
                    'growth_percentage': stars_vel.get('growth_percentage', 0),
                    'current_stars': github.get('latest_values', {}).get('stars', 0)
                })

        # Sort by growth rate
        emerging.sort(key=lambda x: x.get('growth_percentage', 0), reverse=True)
        return emerging

    def detect_declining_technologies(self, velocity_data: Dict) -> List[Dict]:
        """
        Detect declining technologies

        Args:
            velocity_data: Velocity report

        Returns:
            List of declining technologies
        """
        velocities = velocity_data.get('velocities', [])
        declining = []

        for tech in velocities:
            github = tech.get('github', {})
            if 'error' in github:
                continue

            metrics = github.get('metrics', {})
            stars_vel = metrics.get('stars_velocity', {})

            if stars_vel.get('velocity_type') in ['declining', 'collapsing']:
                declining.append({
                    'technology': tech['technology'],
                    'category': tech.get('category', 'unknown'),
                    'velocity_type': stars_vel.get('velocity_type'),
                    'growth_percentage': stars_vel.get('growth_percentage', 0),
                    'current_stars': github.get('latest_values', {}).get('stars', 0)
                })

        return declining

    def generate_executive_summary(self, insights: Dict) -> str:
        """
        Generate executive summary text

        Args:
            insights: Full insights dictionary

        Returns:
            Executive summary string
        """
        summary_parts = []

        # Top leader
        if insights.get('adoption_leaders'):
            leader = insights['adoption_leaders'][0]
            summary_parts.append(
                f"**Leading adoption:** {leader['technology']} ({leader['category']}) "
                f"with {leader['momentum_score']:.1f}% monthly growth momentum."
            )

        # Emerging count
        emerging_count = len(insights.get('emerging_technologies', []))
        if emerging_count > 0:
            summary_parts.append(
                f"**{emerging_count} technologies** showing rapid acceleration or emergence."
            )

        # Hype detection
        hype_count = len(insights.get('hype_detected', []))
        if hype_count > 0:
            summary_parts.append(
                f"**⚠️ {hype_count} hype signals** detected - high visibility but low actual usage."
            )

        # Category insights
        if insights.get('category_trends'):
            sorted_cats = sorted(
                insights['category_trends'].items(),
                key=lambda x: x[1]['average_momentum'],
                reverse=True
            )
            if sorted_cats:
                top_cat = sorted_cats[0]
                summary_parts.append(
                    f"**Fastest category:** {top_cat[0]} averaging {top_cat[1]['average_momentum']:.1f}% growth."
                )

        return "\n\n".join(summary_parts) if summary_parts else "Insufficient data for summary."

    def generate_insights(self, list_name: str) -> Dict:
        """
        Generate comprehensive insights for a list

        Args:
            list_name: List name

        Returns:
            Insights report
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Generating insights for {list_name.upper()}")
        logger.info(f"{'='*60}")

        # Load data
        quality_data = self.load_quality_data(list_name)
        velocity_data = self.load_velocity_data(list_name)

        if not quality_data or not velocity_data:
            logger.error(f"Missing data for {list_name}")
            return {'error': 'insufficient_data'}

        # Generate insights
        insights = {
            'list_name': list_name,
            'generated_at': datetime.now().isoformat(),
            'data_quality_summary': quality_data.get('summary', {}),
        }

        # Adoption leaders
        leaders = self.identify_adoption_leaders(velocity_data, TOP_N_INSIGHTS)
        insights['adoption_leaders'] = leaders
        logger.info(f"\nTop {len(leaders)} adoption leaders identified")
        for i, leader in enumerate(leaders, 1):
            logger.info(f"  {i}. {leader['technology']}: {leader['momentum_score']:.1f}% momentum")

        # Hype detection
        hype = self.identify_hype_candidates(quality_data)
        insights['hype_detected'] = hype
        if hype:
            logger.warning(f"\n⚠️  {len(hype)} hype signals detected:")
            for h in hype:
                logger.warning(f"  - {h['technology']}: {', '.join(h['hype_reasons'])}")

        # Category trends
        category_trends = self.analyze_category_trends(velocity_data)
        insights['category_trends'] = category_trends
        logger.info(f"\nCategory analysis:")
        for cat, data in sorted(category_trends.items(), key=lambda x: x[1]['average_momentum'], reverse=True):
            logger.info(f"  {cat}: {data['average_momentum']:.1f}% avg momentum ({data['technology_count']} techs)")

        # Emerging technologies
        emerging = self.detect_emerging_technologies(velocity_data)
        insights['emerging_technologies'] = emerging
        if emerging:
            logger.info(f"\n🚀 {len(emerging)} emerging technologies:")
            for tech in emerging[:5]:
                logger.info(f"  - {tech['technology']}: {tech['growth_percentage']:.1f}% growth")

        # Declining technologies
        declining = self.detect_declining_technologies(velocity_data)
        insights['declining_technologies'] = declining
        if declining:
            logger.info(f"\n📉 {len(declining)} declining technologies")

        # Executive summary
        insights['executive_summary'] = self.generate_executive_summary(insights)

        logger.info(f"\n{'='*60}")
        logger.info("EXECUTIVE SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"\n{insights['executive_summary']}")

        return insights


def generate_all_insights() -> Dict[str, Dict]:
    """
    Generate insights for all lists

    Returns:
        Dictionary mapping list names to insights
    """
    from ..utils.config import ACTIVE_LISTS

    generator = InsightGenerator()
    results = {}

    for list_name in ACTIVE_LISTS.keys():
        insights = generator.generate_insights(list_name)
        results[list_name] = insights

        # Save insights
        output_file = PROCESSED_DATA_DIR / f'insights_{list_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2)
        logger.info(f"\nSaved insights to {output_file}")

    return results


if __name__ == "__main__":
    print("Generating strategic insights...")
    results = generate_all_insights()
    print("\n✓ Insight generation complete")

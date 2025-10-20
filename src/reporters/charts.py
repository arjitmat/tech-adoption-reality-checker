"""
Visualization Module
Creates charts and graphs for technology adoption reports
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

from ..utils.config import PROCESSED_DATA_DIR, REPORTS_DIR
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class ChartGenerator:
    """Generates visualizations for adoption reports"""

    def __init__(self):
        """Initialize chart generator"""
        self.processed_dir = PROCESSED_DATA_DIR
        self.reports_dir = REPORTS_DIR
        self.charts_dir = self.reports_dir / 'charts'
        self.charts_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')

    def load_latest_file(self, pattern: str) -> Optional[Dict]:
        """Load the most recent file matching pattern"""
        files = sorted(self.processed_dir.glob(pattern), reverse=True)
        if not files:
            return None

        with open(files[0], 'r') as f:
            return json.load(f)

    def create_quality_chart(self, list_name: str) -> Optional[Path]:
        """Create data quality visualization"""
        quality_data = self.load_latest_file('quality_validation_*.json')
        if not quality_data:
            return None

        list_data = quality_data.get(list_name, {})
        summary = list_data.get('summary', {})

        # Data
        categories = ['High\nConfidence', 'Medium\nConfidence', 'Low\nConfidence', 'Hype\nDetected']
        values = [
            summary.get('high_confidence', 0),
            summary.get('medium_confidence', 0),
            summary.get('low_confidence', 0),
            summary.get('hype_detected', 0)
        ]
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#9b59b6']

        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(categories, values, color=colors, alpha=0.8, edgecolor='black')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold', fontsize=12)

        ax.set_ylabel('Number of Technologies', fontsize=12, fontweight='bold')
        ax.set_title(f'{list_name.title()} - Data Quality Distribution', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 1)

        plt.tight_layout()

        # Save
        output_path = self.charts_dir / f'{list_name}_quality_chart.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Created quality chart: {output_path.name}")
        return output_path

    def create_category_momentum_chart(self, list_name: str) -> Optional[Path]:
        """Create category momentum comparison chart"""
        insights = self.load_latest_file(f'insights_{list_name}_*.json')
        if not insights or 'error' in insights:
            return None

        category_trends = insights.get('category_trends', {})
        if not category_trends:
            return None

        # Sort categories by momentum
        sorted_cats = sorted(
            category_trends.items(),
            key=lambda x: x[1].get('average_momentum', 0),
            reverse=True
        )[:8]  # Top 8 categories

        categories = [cat.replace('_', ' ').title() for cat, _ in sorted_cats]
        momenta = [data.get('average_momentum', 0) for _, data in sorted_cats]
        colors = ['#3498db' if m > 0 else '#e74c3c' for m in momenta]

        # Create chart
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(categories, momenta, color=colors, alpha=0.8, edgecolor='black')

        # Add value labels
        for i, (bar, momentum) in enumerate(zip(bars, momenta)):
            width = bar.get_width()
            label_x = width + (max(momenta) * 0.02) if width >= 0 else width - (max(momenta) * 0.02)
            ax.text(label_x, bar.get_y() + bar.get_height()/2.,
                   f'{momentum:.1f}%',
                   ha='left' if width >= 0 else 'right',
                   va='center', fontweight='bold', fontsize=10)

        ax.set_xlabel('Average Monthly Momentum (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{list_name.title()} - Category Momentum Analysis', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)

        plt.tight_layout()

        # Save
        output_path = self.charts_dir / f'{list_name}_category_momentum.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Created category momentum chart: {output_path.name}")
        return output_path

    def create_top_technologies_chart(self, list_name: str) -> Optional[Path]:
        """Create top technologies by stars chart"""
        quality_data = self.load_latest_file('quality_validation_*.json')
        if not quality_data:
            return None

        list_data = quality_data.get(list_name, {})
        technologies = list_data.get('technologies', [])

        # Extract GitHub stars
        tech_stars = []
        for tech in technologies:
            github_data = tech.get('metrics', {}).get('github', {})
            stars = github_data.get('stars', 0)
            if stars > 0:
                tech_stars.append({
                    'name': tech['technology'],
                    'stars': stars
                })

        if not tech_stars:
            return None

        # Sort and get top 10
        tech_stars.sort(key=lambda x: x['stars'], reverse=True)
        top_10 = tech_stars[:10]

        names = [t['name'] for t in top_10]
        stars = [t['stars'] for t in top_10]

        # Create chart
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(names, stars, color='#3498db', alpha=0.8, edgecolor='black')

        # Add value labels
        for bar in bars:
            width = bar.get_width()
            label = f'{int(width/1000)}K' if width >= 1000 else str(int(width))
            ax.text(width + (max(stars) * 0.01), bar.get_y() + bar.get_height()/2.,
                   label,
                   ha='left', va='center', fontweight='bold', fontsize=10)

        ax.set_xlabel('GitHub Stars', fontsize=12, fontweight='bold')
        ax.set_title(f'{list_name.title()} - Top Technologies by GitHub Stars', fontsize=14, fontweight='bold')

        plt.tight_layout()

        # Save
        output_path = self.charts_dir / f'{list_name}_top_technologies.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Created top technologies chart: {output_path.name}")
        return output_path

    def create_comparative_velocity_chart(self) -> Optional[Path]:
        """Create comparative velocity chart between lists"""
        comparative = self.load_latest_file('comparative_analysis_*.json')
        if not comparative or 'error' in comparative:
            return None

        velocity = comparative.get('velocity_comparison', {})
        if 'error' in velocity:
            return None

        lists = comparative.get('lists_compared', ['List 1', 'List 2'])

        # Data
        categories = [lists[0].title(), lists[1].title()]
        avg_momenta = [
            velocity.get(f'{lists[0]}_average_momentum', 0),
            velocity.get(f'{lists[1]}_average_momentum', 0)
        ]
        colors = ['#3498db', '#e67e22']

        # Create chart
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(categories, avg_momenta, color=colors, alpha=0.8, edgecolor='black', width=0.6)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontweight='bold', fontsize=12)

        ax.set_ylabel('Average Monthly Momentum (%)', fontsize=12, fontweight='bold')
        ax.set_title('Comparative Adoption Velocity', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(avg_momenta) * 1.2 if max(avg_momenta) > 0 else 1)

        plt.tight_layout()

        # Save
        output_path = self.charts_dir / 'comparative_velocity.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Created comparative velocity chart: {output_path.name}")
        return output_path

    def generate_all_charts(self) -> Dict[str, List[Path]]:
        """Generate all visualization charts"""
        logger.info("Generating visualization charts...")
        charts = {}

        # Enterprise charts
        logger.info("\nGenerating enterprise charts...")
        enterprise_charts = []
        if chart := self.create_quality_chart('enterprise'):
            enterprise_charts.append(chart)
        if chart := self.create_category_momentum_chart('enterprise'):
            enterprise_charts.append(chart)
        if chart := self.create_top_technologies_chart('enterprise'):
            enterprise_charts.append(chart)
        charts['enterprise'] = enterprise_charts

        # Fintech charts
        logger.info("\nGenerating fintech charts...")
        fintech_charts = []
        if chart := self.create_quality_chart('fintech'):
            fintech_charts.append(chart)
        if chart := self.create_category_momentum_chart('fintech'):
            fintech_charts.append(chart)
        if chart := self.create_top_technologies_chart('fintech'):
            fintech_charts.append(chart)
        charts['fintech'] = fintech_charts

        # Comparative charts
        logger.info("\nGenerating comparative charts...")
        comparative_charts = []
        if chart := self.create_comparative_velocity_chart():
            comparative_charts.append(chart)
        charts['comparative'] = comparative_charts

        logger.info(f"\n✓ Generated {sum(len(v) for v in charts.values())} charts total")
        return charts


if __name__ == "__main__":
    print("Generating visualization charts...")
    generator = ChartGenerator()
    charts = generator.generate_all_charts()

    print("\nGenerated charts:")
    for category, chart_list in charts.items():
        print(f"\n{category.title()}:")
        for chart_path in chart_list:
            print(f"  - {chart_path.name}")

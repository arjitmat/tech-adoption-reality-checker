"""
Report Generator
Creates markdown reports from analyzed data
Generates 3 strategic reports: Enterprise AI, Fintech AI, Comparative Insights
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from ..utils.config import PROCESSED_DATA_DIR, REPORTS_DIR
from ..utils.logger import get_default_logger

logger = get_default_logger(__name__)


class ReportGenerator:
    """Generates strategic markdown reports from analysis data"""

    def __init__(self):
        """Initialize report generator"""
        self.processed_dir = PROCESSED_DATA_DIR
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_latest_file(self, pattern: str) -> Optional[Dict]:
        """Load the most recent file matching pattern"""
        files = sorted(self.processed_dir.glob(pattern), reverse=True)
        if not files:
            logger.warning(f"No files found matching {pattern}")
            return None

        with open(files[0], 'r') as f:
            return json.load(f)

    def format_number(self, num: float, decimals: int = 1) -> str:
        """Format number for display"""
        if num == float('inf'):
            return "∞"
        if abs(num) >= 1000000:
            return f"{num/1000000:.{decimals}f}M"
        if abs(num) >= 1000:
            return f"{num/1000:.{decimals}f}K"
        return f"{num:.{decimals}f}"

    def generate_header(self, title: str, subtitle: str = None) -> str:
        """Generate report header"""
        lines = [
            f"# {title}",
            "",
        ]
        if subtitle:
            lines.extend([f"**{subtitle}**", ""])

        lines.extend([
            f"*Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}*",
            "",
            "---",
            ""
        ])
        return "\n".join(lines)

    def generate_quality_section(self, quality_data: Dict) -> str:
        """Generate data quality section"""
        summary = quality_data.get('summary', {})
        total = quality_data.get('total_technologies', 0)

        lines = [
            "## Data Quality Overview",
            "",
            f"**Total Technologies Analyzed:** {total}",
            "",
            "### Confidence Distribution",
            f"- 🟢 **High Confidence:** {summary.get('high_confidence', 0)} technologies (2+ sources)",
            f"- 🟡 **Medium Confidence:** {summary.get('medium_confidence', 0)} technologies (1 source)",
            f"- 🔴 **Low Confidence:** {summary.get('low_confidence', 0)} technologies",
            "",
        ]

        # Hype detection
        hype_count = summary.get('hype_detected', 0)
        if hype_count > 0:
            lines.extend([
                f"### ⚠️ Hype Signals Detected: {hype_count}",
                "",
                "Technologies showing divergence between visibility and actual usage:",
                ""
            ])

            technologies = quality_data.get('technologies', [])
            for tech in technologies:
                if tech.get('hype_detected'):
                    lines.append(f"- **{tech['technology']}**: {', '.join(tech['hype_reasons'])}")

            lines.append("")

        return "\n".join(lines)

    def generate_insights_section(self, insights_data: Dict) -> str:
        """Generate insights section"""
        if not insights_data or 'error' in insights_data:
            return "## Insights\n\n*Insufficient data for insights generation.*\n\n"

        lines = [
            "## Executive Summary",
            "",
            insights_data.get('executive_summary', '*Analyzing trends...*'),
            "",
            "---",
            ""
        ]

        # Adoption leaders
        leaders = insights_data.get('adoption_leaders', [])
        if leaders:
            lines.extend([
                "## 🚀 Adoption Leaders",
                "",
                "Technologies showing strongest growth momentum:",
                ""
            ])

            for i, leader in enumerate(leaders[:5], 1):
                momentum = leader.get('momentum_score', 0)
                stars = self.format_number(leader.get('github_stars', 0), 0)
                category = leader.get('category', 'unknown')
                velocity_type = leader.get('velocity_type', 'unknown')

                lines.append(
                    f"{i}. **{leader['technology']}** ({category})"
                )
                lines.append(f"   - Momentum: {momentum:.1f}% monthly growth")
                lines.append(f"   - GitHub Stars: {stars}")
                lines.append(f"   - Trend: {velocity_type.replace('_', ' ').title()}")
                lines.append("")

        # Category trends
        category_trends = insights_data.get('category_trends', {})
        if category_trends:
            lines.extend([
                "## 📊 Category Analysis",
                "",
            ])

            sorted_categories = sorted(
                category_trends.items(),
                key=lambda x: x[1].get('average_momentum', 0),
                reverse=True
            )

            lines.append("| Category | Tech Count | Avg Momentum | Top Technology |")
            lines.append("|----------|------------|--------------|----------------|")

            for category, data in sorted_categories:
                tech_count = data.get('technology_count', 0)
                avg_momentum = data.get('average_momentum', 0)
                technologies = data.get('technologies', [])
                top_tech = technologies[0]['technology'] if technologies else 'N/A'

                lines.append(
                    f"| {category.replace('_', ' ').title()} | "
                    f"{tech_count} | "
                    f"{avg_momentum:.1f}% | "
                    f"{top_tech} |"
                )

            lines.append("")

        # Emerging technologies
        emerging = insights_data.get('emerging_technologies', [])
        if emerging:
            lines.extend([
                "## 🌟 Emerging Technologies",
                "",
                "Rapid acceleration or new emergence detected:",
                ""
            ])

            for tech in emerging[:5]:
                growth = tech.get('growth_percentage', 0)
                stars = self.format_number(tech.get('current_stars', 0), 0)
                lines.append(f"- **{tech['technology']}**: {growth:.1f}% growth ({stars} stars)")

            lines.append("")

        # Declining technologies
        declining = insights_data.get('declining_technologies', [])
        if declining:
            lines.extend([
                "## 📉 Declining Adoption",
                "",
            ])

            for tech in declining[:3]:
                growth = tech.get('growth_percentage', 0)
                lines.append(f"- **{tech['technology']}**: {growth:.1f}% decline")

            lines.append("")

        return "\n".join(lines)

    def generate_list_report(self, list_name: str) -> str:
        """
        Generate report for a specific list

        Args:
            list_name: List name (enterprise/fintech)

        Returns:
            Markdown report content
        """
        logger.info(f"Generating {list_name} report...")

        # Load data
        quality_data = self.load_latest_file(f'quality_validation_*.json')
        quality_list_data = quality_data.get(list_name, {}) if quality_data else {}

        insights_data = self.load_latest_file(f'insights_{list_name}_*.json')

        # Generate report sections
        if list_name == 'enterprise':
            title = "Enterprise AI Adoption Report"
            subtitle = "Strategic Analysis of AI Platform & Infrastructure Adoption"
        elif list_name == 'fintech':
            title = "Fintech AI Landscape Report"
            subtitle = "Technology Adoption in Financial Services & Trading"
        else:
            title = f"{list_name.title()} Technology Report"
            subtitle = None

        report = []
        report.append(self.generate_header(title, subtitle))

        # Overview
        report.append("## Overview")
        report.append("")
        if list_name == 'enterprise':
            report.append("This report analyzes adoption trends across enterprise AI platforms, infrastructure, and ML tools. "
                         "Focus areas include major AI platforms (OpenAI, Anthropic, Google), vector databases, "
                         "and enterprise ML infrastructure.")
        elif list_name == 'fintech':
            report.append("This report analyzes AI and technology adoption specifically within financial services, "
                         "trading, and fintech applications. Covers payment infrastructure, quantitative tools, "
                         "and risk/compliance systems.")
        report.append("")
        report.append("---")
        report.append("")

        # Quality section
        if quality_list_data:
            report.append(self.generate_quality_section(quality_list_data))
            report.append("---")
            report.append("")

        # Insights section
        if insights_data:
            report.append(self.generate_insights_section(insights_data))

        # Footer
        report.append("---")
        report.append("")
        report.append("## Methodology")
        report.append("")
        report.append("**Data Sources:**")
        report.append("- GitHub API: Repository metrics (stars, forks, commits)")
        report.append("- npm registry: JavaScript package downloads")
        report.append("- PyPI: Python package statistics")
        report.append("")
        report.append("**Analysis:**")
        report.append("- Multi-source validation for data quality")
        report.append("- Velocity-based momentum calculations")
        report.append("- Hype detection through signal divergence")
        report.append("")
        report.append("**Note:** Velocity analysis improves with historical data accumulation.")
        report.append("")

        return "\n".join(report)

    def generate_comparative_report(self) -> str:
        """Generate comparative insights report"""
        logger.info("Generating comparative insights report...")

        # Load data
        comparative_data = self.load_latest_file('comparative_analysis_*.json')

        if not comparative_data or 'error' in comparative_data:
            logger.warning("Insufficient data for comparative report")
            return self._generate_placeholder_comparative_report()

        # Generate report
        report = []
        report.append(self.generate_header(
            "Comparative Technology Adoption Insights",
            "Cross-Market Analysis: Enterprise AI vs Fintech AI"
        ))

        # Overview
        lists = comparative_data.get('lists_compared', ['List 1', 'List 2'])
        report.extend([
            "## Overview",
            "",
            "This report synthesizes insights across two strategic technology dimensions:",
            "",
            f"1. **{lists[0].upper()}**: Enterprise AI platforms and infrastructure",
            f"2. **{lists[1].upper()}**: Fintech and trading-specific technologies",
            "",
            "**Why Comparative Analysis?**",
            "",
            "Cross-market pattern detection reveals insights impossible from single-dimension tracking:",
            "- Adoption lag patterns (which market leads)",
            "- Leading indicators (technology X predicts technology Y)",
            "- Category-specific divergence (enterprise vs fintech priorities)",
            "- Strategic timing windows for technology investments",
            "",
            "---",
            ""
        ])

        # Strategic insights
        strategic_insights = comparative_data.get('strategic_insights', [])
        if strategic_insights:
            report.extend([
                "## 🎯 Key Strategic Insights",
                ""
            ])
            for i, insight in enumerate(strategic_insights, 1):
                report.append(f"{i}. {insight}")
            report.append("")
            report.append("---")
            report.append("")

        # Velocity comparison
        velocity = comparative_data.get('velocity_comparison', {})
        if velocity and 'error' not in velocity:
            report.extend([
                "## Adoption Velocity Comparison",
                "",
                f"**Finding:** {velocity.get('interpretation', 'Analyzing...')}",
                "",
                f"- **{lists[0].title()} average momentum:** {velocity.get(f'{lists[0]}_average_momentum', 0):.1f}%",
                f"- **{lists[1].title()} average momentum:** {velocity.get(f'{lists[1]}_average_momentum', 0):.1f}%",
                f"- **Velocity difference:** {velocity.get('velocity_difference_percentage', 0):.1f}%",
                "",
                "---",
                ""
            ])

        # Category patterns
        category_patterns = comparative_data.get('category_patterns', {})
        if category_patterns:
            unique1 = category_patterns.get('unique_to_list1', [])
            unique2 = category_patterns.get('unique_to_list2', [])
            shared = category_patterns.get('shared_categories', [])

            report.extend([
                "## Technology Focus Patterns",
                "",
                f"### Unique to {lists[0].title()}",
                ""
            ])

            if unique1:
                for cat in unique1:
                    report.append(f"- **{cat['category'].replace('_', ' ').title()}**: "
                                f"{cat['tech_count']} technologies, "
                                f"{cat['momentum']:.1f}% avg momentum")
            else:
                report.append("*No unique categories*")

            report.extend(["", f"### Unique to {lists[1].title()}", ""])

            if unique2:
                for cat in unique2:
                    report.append(f"- **{cat['category'].replace('_', ' ').title()}**: "
                                f"{cat['tech_count']} technologies, "
                                f"{cat['momentum']:.1f}% avg momentum")
            else:
                report.append("*No unique categories*")

            report.extend(["", f"### Shared Categories: {len(shared)}", ""])
            report.append("---")
            report.append("")

        # Leading indicators
        indicators = comparative_data.get('leading_indicators', [])
        if indicators:
            report.extend([
                "## 🔮 Leading Indicator Patterns",
                "",
                "Potential predictive relationships detected:",
                ""
            ])

            for indicator in indicators:
                report.append(f"**{indicator['indicator_type'].replace('_', ' ').title()}**")
                report.append(f"- {indicator['hypothesis']}")
                report.append(f"- Confidence: {indicator['confidence']}")
                report.append("")

            report.append("---")
            report.append("")

        # Adoption lag
        lag = comparative_data.get('adoption_lag', {})
        if lag:
            report.extend([
                "## ⏱️ Market Maturity & Adoption Lag",
                "",
                f"**{lag.get('interpretation', 'Analyzing market maturity...')}**",
                "",
                f"- {lists[0].title()} maturity score: {lag.get(f'{lists[0]}_maturity_score', 0):.1f}",
                f"- {lists[1].title()} maturity score: {lag.get(f'{lists[1]}_maturity_score', 0):.1f}",
                "",
                f"*{lag.get('note', '')}*",
                "",
                "---",
                ""
            ])

        # Methodology
        report.extend([
            "## Methodology",
            "",
            "**Comparative Analysis Approach:**",
            "1. Independent analysis of each technology list",
            "2. Cross-market velocity comparison",
            "3. Category-level pattern identification",
            "4. Leading indicator hypothesis generation",
            "5. Adoption lag estimation via maturity proxies",
            "",
            "**Data Foundation:**",
            "- Multi-source validation (GitHub + npm + PyPI)",
            "- Quality-scored insights (high confidence required)",
            "- Time-series analysis (improves with data accumulation)",
            "",
            "**Note:** This analysis becomes more powerful with historical data. "
            "Initial insights based on current snapshot; patterns strengthen over time.",
            ""
        ])

        return "\n".join(report)

    def _generate_placeholder_comparative_report(self) -> str:
        """Generate placeholder when comparative data insufficient"""
        report = []
        report.append(self.generate_header(
            "Comparative Technology Adoption Insights",
            "Cross-Market Analysis: Enterprise AI vs Fintech AI"
        ))

        report.extend([
            "## 🚧 Analysis In Progress",
            "",
            "Comparative insights require:",
            "- ✅ Data collection from both markets (complete)",
            "- ⏳ Historical data accumulation (in progress)",
            "- ⏳ Velocity trend establishment",
            "",
            "**Current Status:**",
            "- Data collection: Operational",
            "- Quality validation: Complete",
            "- Comparative framework: Ready",
            "",
            "**Next Steps:**",
            "System will generate deeper comparative insights as data accumulates over time. "
            "Check back after system runs for several days to see:",
            "",
            "- Cross-market adoption lag quantification",
            "- Leading indicator patterns",
            "- Category-specific trends",
            "- Strategic timing windows",
            "",
            "---",
            "",
            "## Framework Overview",
            "",
            "This comparative analysis will track:",
            "",
            "1. **Enterprise AI** (15 technologies)",
            "   - AI platforms, infrastructure, ML tools",
            "   - What enterprises actually deploy",
            "",
            "2. **Fintech AI** (12 technologies)",
            "   - Financial services, trading, risk/compliance",
            "   - Domain-specific adoption patterns",
            "",
            "**Unique Insights To Come:**",
            "- \"Fintech AI adoption lags enterprise by X months\"",
            "- \"Vector DB adoption predicts LLM deployment\"",
            "- \"Fintech prioritizes risk/compliance over customer tools\"",
            "",
        ])

        return "\n".join(report)

    def save_report(self, content: str, filename: str) -> Path:
        """Save report to file"""
        output_path = self.reports_dir / filename
        with open(output_path, 'w') as f:
            f.write(content)
        logger.info(f"Report saved to {output_path}")
        return output_path


def generate_all_reports() -> Dict[str, Path]:
    """
    Generate all strategic reports

    Returns:
        Dictionary mapping report names to file paths
    """
    generator = ReportGenerator()
    reports = {}

    # Enterprise report
    logger.info("\n" + "="*60)
    logger.info("GENERATING ENTERPRISE AI REPORT")
    logger.info("="*60)
    enterprise_content = generator.generate_list_report('enterprise')
    enterprise_path = generator.save_report(
        enterprise_content,
        f'enterprise_ai_report_{datetime.now().strftime("%Y%m%d")}.md'
    )
    reports['enterprise'] = enterprise_path

    # Fintech report
    logger.info("\n" + "="*60)
    logger.info("GENERATING FINTECH AI REPORT")
    logger.info("="*60)
    fintech_content = generator.generate_list_report('fintech')
    fintech_path = generator.save_report(
        fintech_content,
        f'fintech_ai_report_{datetime.now().strftime("%Y%m%d")}.md'
    )
    reports['fintech'] = fintech_path

    # Comparative report
    logger.info("\n" + "="*60)
    logger.info("GENERATING COMPARATIVE INSIGHTS REPORT")
    logger.info("="*60)
    comparative_content = generator.generate_comparative_report()
    comparative_path = generator.save_report(
        comparative_content,
        f'comparative_insights_{datetime.now().strftime("%Y%m%d")}.md'
    )
    reports['comparative'] = comparative_path

    logger.info("\n" + "="*60)
    logger.info("✓ ALL REPORTS GENERATED")
    logger.info("="*60)

    return reports


if __name__ == "__main__":
    print("Generating strategic reports...")
    reports = generate_all_reports()
    print("\nGenerated reports:")
    for name, path in reports.items():
        print(f"  {name}: {path.name}")

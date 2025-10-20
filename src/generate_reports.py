"""
Main report generation script
Generates all strategic reports and visualizations
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporters.generate import generate_all_reports
from src.reporters.charts import ChartGenerator
from src.utils.logger import get_default_logger

logger = get_default_logger(__name__)


def main():
    """Generate all reports and visualizations"""
    logger.info("="*70)
    logger.info("TECH ADOPTION REPORT GENERATION - STARTING")
    logger.info("="*70)

    # Generate charts
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 1: GENERATING VISUALIZATIONS")
        logger.info("="*70)
        chart_gen = ChartGenerator()
        charts = chart_gen.generate_all_charts()
        logger.info("✓ Visualizations completed")
    except Exception as e:
        logger.error(f"✗ Visualization generation failed: {e}")
        charts = {}

    # Generate reports
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 2: GENERATING MARKDOWN REPORTS")
        logger.info("="*70)
        reports = generate_all_reports()
        logger.info("✓ Reports completed")
    except Exception as e:
        logger.error(f"✗ Report generation failed: {e}")
        reports = {}

    # Summary
    logger.info("\n" + "="*70)
    logger.info("REPORT GENERATION COMPLETE")
    logger.info("="*70)

    if reports:
        logger.info("\nGenerated Reports:")
        for name, path in reports.items():
            logger.info(f"  {name.upper()}: {path.name}")

    if charts:
        total_charts = sum(len(v) for v in charts.values())
        logger.info(f"\nGenerated Charts: {total_charts} total")

    logger.info("\n" + "="*70)

    return {'reports': reports, 'charts': charts}


if __name__ == "__main__":
    results = main()

    if results.get('reports'):
        print("\n✓ Report generation successful!")
        print(f"\nReports location: reports/")
        print("Charts location: reports/charts/")
    else:
        print("\n⚠ Report generation incomplete. Check logs for details.")

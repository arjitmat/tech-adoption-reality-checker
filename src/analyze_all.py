"""
Main analysis script
Orchestrates quality validation, velocity calculation, insights, and comparative analysis
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzers.quality import validate_all_lists
from src.analyzers.velocity import calculate_all_velocities
from src.analyzers.insights import generate_all_insights
from src.analyzers.comparative import generate_comparative_analysis
from src.utils.logger import get_default_logger

logger = get_default_logger(__name__)


def run_full_analysis():
    """
    Run complete analysis pipeline
    """
    logger.info("="*70)
    logger.info("TECH ADOPTION ANALYSIS PIPELINE - STARTING")
    logger.info("="*70)

    # Step 1: Data Quality Validation
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 1: DATA QUALITY VALIDATION")
        logger.info("="*70)
        quality_results = validate_all_lists()
        logger.info("✓ Quality validation completed")
    except Exception as e:
        logger.error(f"✗ Quality validation failed: {e}")
        quality_results = None

    # Step 2: Velocity Calculation
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 2: VELOCITY CALCULATION")
        logger.info("="*70)
        velocity_results = calculate_all_velocities()
        logger.info("✓ Velocity calculation completed")
    except Exception as e:
        logger.error(f"✗ Velocity calculation failed: {e}")
        velocity_results = None

    # Step 3: Insight Generation
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 3: INSIGHT GENERATION")
        logger.info("="*70)
        insight_results = generate_all_insights()
        logger.info("✓ Insight generation completed")
    except Exception as e:
        logger.error(f"✗ Insight generation failed: {e}")
        insight_results = None

    # Step 4: Comparative Analysis
    try:
        logger.info("\n" + "="*70)
        logger.info("STEP 4: COMPARATIVE ANALYSIS")
        logger.info("="*70)
        comparative_results = generate_comparative_analysis()
        logger.info("✓ Comparative analysis completed")
    except Exception as e:
        logger.error(f"✗ Comparative analysis failed: {e}")
        comparative_results = None

    # Summary
    logger.info("\n" + "="*70)
    logger.info("ANALYSIS PIPELINE COMPLETE")
    logger.info("="*70)

    results_summary = {
        'quality_validation': '✓' if quality_results else '✗',
        'velocity_calculation': '✓' if velocity_results else '✗',
        'insight_generation': '✓' if insight_results else '✗',
        'comparative_analysis': '✓' if comparative_results else '✗',
    }

    for step, status in results_summary.items():
        logger.info(f"  {step}: {status}")

    logger.info("\n" + "="*70)

    return {
        'quality': quality_results,
        'velocity': velocity_results,
        'insights': insight_results,
        'comparative': comparative_results
    }


if __name__ == "__main__":
    results = run_full_analysis()

    # Check if all steps succeeded
    all_success = all([
        results.get('quality'),
        results.get('velocity'),
        results.get('insights'),
        results.get('comparative')
    ])

    if all_success:
        print("\n✓ All analysis steps completed successfully!")
        print("\nGenerated files in data/processed/:")
        from pathlib import Path
        from src.utils.config import PROCESSED_DATA_DIR
        for f in sorted(PROCESSED_DATA_DIR.glob('*.json'), reverse=True)[:10]:
            print(f"  - {f.name}")
    else:
        print("\n⚠ Some analysis steps failed. Check logs for details.")

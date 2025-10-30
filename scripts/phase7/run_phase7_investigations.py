#!/usr/bin/env python3
"""
Phase 7 Master Investigation Script
====================================

Run all Phase 7 investigations in sequence or individually.

Usage:
    python run_phase7_investigations.py --all      # Run all 3 investigations
    python run_phase7_investigations.py --y        # Run only y (conjunction)
    python run_phase7_investigations.py --ar       # Run only ar (preposition)
    python run_phase7_investigations.py --daiin    # Run only daiin (particle)

This script coordinates the three main Phase 7 investigations and
generates a summary report at the end.

Author: Voynich Research Team
Date: 2025-10-30
"""

import argparse
import subprocess
import sys
import json
from datetime import datetime


def run_script(script_name, description):
    """Run a single investigation script and capture results"""
    print("\n" + "=" * 80)
    print(f"RUNNING: {description}")
    print("=" * 80)
    print(f"Script: {script_name}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        result = subprocess.run(
            ["python", script_name],
            capture_output=False,  # Show output in real-time
            text=True,
            check=False,  # Don't raise exception on non-zero exit
        )

        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Exit code: {result.returncode}")

        if result.returncode == 0:
            print("✓ Script completed successfully")
            return True
        else:
            print("⚠ Script completed with warnings/errors")
            return False

    except FileNotFoundError:
        print(f"✗ ERROR: Script not found: {script_name}")
        print(f"   Make sure you're in the correct directory")
        return False
    except Exception as e:
        print(f"✗ ERROR running script: {str(e)}")
        return False


def print_header():
    """Print Phase 7 header"""
    print("=" * 80)
    print("PHASE 7: FUNCTION WORDS INVESTIGATION")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("This script will run the following investigations:")
    print("  1. 'y' as conjunction (Polish 'and' parallel)")
    print("  2. 'ar' as locative preposition ('at/in')")
    print("  3. 'daiin' as demonstrative particle ('that/which/it')")
    print()
    print("Each investigation:")
    print("  - Analyzes morphology and distribution")
    print("  - Tests contextual coherence")
    print("  - Applies 12-point validation scoring")
    print("  - Takes 45-90 minutes")
    print()
    print(
        "You will be prompted for manual coherence scoring during each investigation."
    )
    print("=" * 80)
    print()


def print_summary(results):
    """Print summary of all investigations"""
    print("\n" + "=" * 80)
    print("PHASE 7 INVESTIGATION SUMMARY")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    total_run = len(results)
    total_success = sum(1 for r in results.values() if r)

    print(f"Investigations run: {total_run}")
    print(f"Successful runs: {total_success}")
    print()

    print("Results:")
    for investigation, success in results.items():
        status = "✓ Completed" if success else "✗ Failed/Incomplete"
        print(f"  {investigation:30s}: {status}")

    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    if total_success == total_run:
        print("✓✓✓ All investigations completed successfully!")
        print()
        print("Review the validation scores for each term:")
        print("  - 10-12/12: VALIDATED → Add to vocabulary")
        print("  - 8-9/12: LIKELY → Probably correct")
        print("  - 6-7/12: POSSIBLE → Needs more investigation")
        print("  - <6/12: REJECTED → Hypothesis doesn't fit")
        print()
        print("If any terms validated (≥10/12):")
        print(
            "  1. Update translation framework (scripts/phase7/retranslate_with_validated_phase7.py)"
        )
        print("  2. Re-translate sample sentences")
        print("  3. Update documentation:")
        print("     - VOYNICH_COMPLETE_GRAMMAR_REFERENCE.md")
        print("     - SPATIAL_SYSTEM_COMPLETE.md (if 'ar' validated)")
        print("     - DECODING_STATUS_UPDATE.md")
        print("     - README.md")
        print()
        print("Expected improvements:")
        print("  - 3 validated: 50-55% translation (EXCELLENT)")
        print("  - 2 validated: 48-52% translation (VERY GOOD)")
        print("  - 1 validated: 45-48% translation (GOOD)")
        print("  - 0 validated: Still learned methodology! (TRY OTHER CANDIDATES)")
    else:
        print("⚠ Some investigations had issues.")
        print()
        print("Troubleshooting:")
        print("  - Check that you're in the manuscript directory")
        print("  - Ensure Python can find the data files")
        print("  - Review error messages above")
        print()
        print("You can re-run individual investigations:")
        print("  python run_phase7_investigations.py --y")
        print("  python run_phase7_investigations.py --ar")
        print("  python run_phase7_investigations.py --daiin")

    print()
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Run Phase 7 function word investigations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_phase7_investigations.py --all     # Run all investigations
  python run_phase7_investigations.py --y       # Just test 'y' as conjunction
  python run_phase7_investigations.py --ar --daiin  # Test ar and daiin only

Each investigation will prompt you for manual coherence scoring (0-2 points).
Review the sample translations and assess if the hypothesis makes sense.
        """,
    )

    parser.add_argument(
        "--all", action="store_true", help="Run all 3 investigations (y, ar, daiin)"
    )
    parser.add_argument(
        "--y", action="store_true", help="Investigate 'y' as conjunction"
    )
    parser.add_argument(
        "--ar", action="store_true", help="Investigate 'ar' as preposition"
    )
    parser.add_argument(
        "--daiin", action="store_true", help="Investigate 'daiin' as particle"
    )

    args = parser.parse_args()

    # If no arguments, show help
    if not (args.all or args.y or args.ar or args.daiin):
        parser.print_help()
        return

    print_header()

    # Determine which scripts to run
    scripts_to_run = []

    if args.all or args.y:
        scripts_to_run.append(
            (
                "scripts/phase7/investigate_y_conjunction.py",
                "Y as Conjunction Investigation",
            )
        )

    if args.all or args.ar:
        scripts_to_run.append(
            (
                "scripts/phase7/investigate_ar_preposition.py",
                "AR as Preposition Investigation",
            )
        )

    if args.all or args.daiin:
        scripts_to_run.append(
            (
                "scripts/phase7/investigate_daiin_particle.py",
                "DAIIN as Particle Investigation",
            )
        )

    # Run investigations
    results = {}

    for script_path, description in scripts_to_run:
        # Ask user to confirm
        print(f"\n{'=' * 80}")
        print(f"READY TO RUN: {description}")
        print(f"{'=' * 80}")
        print(f"This will take approximately 45-90 minutes.")
        print(f"You will be prompted for manual input at the end.")
        print()

        response = input("Continue? (y/n): ").strip().lower()
        if response != "y":
            print(f"Skipping {description}")
            results[description] = False
            continue

        success = run_script(script_path, description)
        results[description] = success

        if not success:
            print()
            response = (
                input(
                    "Investigation had issues. Continue with remaining investigations? (y/n): "
                )
                .strip()
                .lower()
            )
            if response != "y":
                print("Stopping investigations.")
                break

    # Print summary
    print_summary(results)

    # Save results
    try:
        results_file = "scripts/phase7/phase7_investigation_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "results": {
                        k: ("completed" if v else "failed") for k, v in results.items()
                    },
                    "total_run": len(results),
                    "total_success": sum(1 for r in results.values() if r),
                },
                f,
                indent=2,
            )
        print(f"\nResults saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠ Could not save results file: {str(e)}")


if __name__ == "__main__":
    main()

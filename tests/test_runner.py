#!/usr/bin/env python3
"""
eRTMAC-NWIS Standalone Test Runner
Executes E2E test suites by tier or full run.
Usage:
    python3 tests/test_runner.py --tier 1
    python3 tests/test_runner.py --tier 2
    python3 tests/test_runner.py --tier 3
    python3 tests/test_runner.py --tier 4
    python3 tests/test_runner.py --tier all
"""

import argparse
import os
import sys
import time
import unittest

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def get_tier_dir(tier: str) -> str:
    mapping = {
        "1": os.path.join(SCRIPT_DIR, "tier1_features"),
        "tier1": os.path.join(SCRIPT_DIR, "tier1_features"),
        "2": os.path.join(SCRIPT_DIR, "tier2_boundaries"),
        "tier2": os.path.join(SCRIPT_DIR, "tier2_boundaries"),
        "3": os.path.join(SCRIPT_DIR, "tier3_combinations"),
        "tier3": os.path.join(SCRIPT_DIR, "tier3_combinations"),
        "4": os.path.join(SCRIPT_DIR, "tier4_scenarios"),
        "tier4": os.path.join(SCRIPT_DIR, "tier4_scenarios"),
    }
    return mapping.get(tier.lower().strip())


def run_tier(tier_name: str, test_dir: str, verbosity: int = 1) -> unittest.TestResult:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
    
    print(f"\n{'='*70}")
    print(f"  RUNNING TIER {tier_name.upper()}: {os.path.basename(test_dir)}")
    print(f"  Test Discovery Path: {test_dir}")
    print(f"  Total Test Cases Discovered: {suite.countTestCases()}")
    print(f"{'='*70}\n")
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result


def main():
    parser = argparse.ArgumentParser(description="eRTMAC-NWIS E2E Test Suite Runner")
    parser.add_argument(
        "--tier",
        type=str,
        default="all",
        choices=["1", "tier1", "2", "tier2", "3", "tier3", "4", "tier4", "all"],
        help="Specify which test tier to execute (1, 2, 3, 4, or all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose test output"
    )

    args = parser.parse_args()
    verbosity = 2 if args.verbose else 1

    total_runs = 0
    total_failures = 0
    total_errors = 0
    start_time = time.perf_counter()

    tiers_to_run = []
    if args.tier == "all":
        tiers_to_run = ["1", "2", "3", "4"]
    else:
        norm_tier = args.tier.replace("tier", "")
        tiers_to_run = [norm_tier]

    print(f"\n=======================================================")
    print(f"  eRTMAC-NWIS Test Suite Runner")
    print(f"  Selected Tier(s): {', '.join(tiers_to_run)}")
    print(f"  Environment: Python {sys.version.split()[0]}")
    print(f"=======================================================")

    results_summary = []

    for t in tiers_to_run:
        target_dir = get_tier_dir(t)
        if not target_dir or not os.path.exists(target_dir):
            print(f"Error: Directory for Tier {t} not found: {target_dir}")
            sys.exit(1)

        tier_start = time.perf_counter()
        result = run_tier(t, target_dir, verbosity=verbosity)
        tier_elapsed = time.perf_counter() - tier_start

        total_runs += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)

        tier_status = "PASSED" if (len(result.failures) == 0 and len(result.errors) == 0) else "FAILED"
        results_summary.append({
            "tier": f"Tier {t}",
            "tests": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "status": tier_status,
            "duration": tier_elapsed
        })

    total_elapsed = time.perf_counter() - start_time

    print(f"\n\n{'#'*70}")
    print(f"                    TEST RUN SUMMARY REPORT")
    print(f"{'#'*70}")
    print(f"{'Tier':<10} | {'Tests':<8} | {'Failures':<10} | {'Errors':<8} | {'Duration (s)':<12} | {'Status'}")
    print(f"{'-'*70}")
    for s in results_summary:
        print(f"{s['tier']:<10} | {s['tests']:<8} | {s['failures']:<10} | {s['errors']:<8} | {s['duration']:<12.3f} | {s['status']}")
    print(f"{'-'*70}")
    print(f"TOTAL TESTS RUN: {total_runs}")
    print(f"TOTAL FAILURES:  {total_failures}")
    print(f"TOTAL ERRORS:    {total_errors}")
    print(f"TOTAL DURATION:  {total_elapsed:.3f} seconds")
    print(f"{'#'*70}\n")

    if total_failures > 0 or total_errors > 0:
        print(f"❌ TEST SUITE RUN FAILED ({total_failures} failures, {total_errors} errors)")
        sys.exit(1)
    else:
        print(f"✅ ALL {total_runs} TESTS PASSED CLEANLY (100% PASS RATE)")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Behavioral Test Runner

Runs the M1 behavioral test suite with various options:
- smoke: Quick smoke tests (5 minutes)
- strategy: Strategy selection tests (15 minutes)
- identity: Identity preservation tests (20 minutes)
- tiers: Tier differentiation tests (15 minutes)
- performance: Processing characteristics tests (10 minutes)
- edge: Edge case tests (10 minutes)
- full: All tests (~75 minutes)

Usage:
    python run_behavioral_tests.py smoke
    python run_behavioral_tests.py full
    python run_behavioral_tests.py strategy identity
    python run_behavioral_tests.py --coverage
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


TEST_SUITES = {
    "smoke": {
        "files": [
            "test_strategy_selection.py::TestStrategySelection::test_high_urgency_high_relevance_strategy",
            "test_identity_preservation.py::TestExpertiseInfluencesConfidence::test_expert_has_higher_confidence",
            "test_tier_differentiation.py::TestReflexTier::test_reflex_produces_brief_output",
        ],
        "description": "Quick smoke tests",
        "estimated_time": "5 minutes",
    },
    "strategy": {
        "files": ["test_strategy_selection.py"],
        "description": "Strategy selection tests",
        "estimated_time": "15 minutes",
    },
    "identity": {
        "files": ["test_identity_preservation.py"],
        "description": "Identity preservation tests",
        "estimated_time": "20 minutes",
    },
    "tiers": {
        "files": ["test_tier_differentiation.py"],
        "description": "Tier differentiation tests",
        "estimated_time": "15 minutes",
    },
    "performance": {
        "files": ["test_processing_characteristics.py"],
        "description": "Processing characteristics tests",
        "estimated_time": "10 minutes",
    },
    "edge": {
        "files": ["test_edge_cases.py"],
        "description": "Edge case tests",
        "estimated_time": "10 minutes",
    },
    "full": {
        "files": [
            "test_strategy_selection.py",
            "test_identity_preservation.py",
            "test_tier_differentiation.py",
            "test_processing_characteristics.py",
            "test_edge_cases.py",
        ],
        "description": "Full test suite",
        "estimated_time": "75 minutes",
    },
}


def run_tests(suites: list, coverage: bool = False, verbose: int = 1):
    """Run specified test suites."""
    
    # Build list of test files
    test_files = []
    for suite in suites:
        if suite in TEST_SUITES:
            test_files.extend(TEST_SUITES[suite]["files"])
        else:
            print(f"Unknown test suite: {suite}")
            print(f"Available suites: {', '.join(TEST_SUITES.keys())}")
            return 1
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add behavioral tests directory
    behavioral_dir = Path(__file__).parent / "behavioral"
    
    # Add test files
    for f in test_files:
        cmd.append(str(behavioral_dir / f))
    
    # Add verbosity
    if verbose >= 2:
        cmd.append("-vv")
    elif verbose >= 1:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Short tracebacks
        "-x",  # Stop on first failure
        "--durations=10",  # Show 10 slowest tests
    ])
    
    # Print info
    print("=" * 70)
    print("M1 BEHAVIORAL TEST RUNNER")
    print("=" * 70)
    print(f"Suites: {', '.join(suites)}")
    
    estimated_time = "Unknown"
    for suite in suites:
        if suite in TEST_SUITES:
            print(f"  - {suite}: {TEST_SUITES[suite]['description']}")
            estimated_time = TEST_SUITES[suite].get("estimated_time", estimated_time)
    
    print(f"Estimated time: {estimated_time}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 70)
    print()
    
    # Run tests
    start_time = time.time()
    result = subprocess.run(cmd)
    elapsed = time.time() - start_time
    
    # Print summary
    print()
    print("=" * 70)
    print(f"COMPLETED in {elapsed:.1f} seconds")
    print(f"Exit code: {result.returncode}")
    print("=" * 70)
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run M1 behavioral tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available test suites:
  smoke       - Quick smoke tests (5 minutes)
  strategy    - Strategy selection tests (15 minutes)
  identity    - Identity preservation tests (20 minutes)
  tiers       - Tier differentiation tests (15 minutes)
  performance - Processing characteristics tests (10 minutes)
  edge        - Edge case tests (10 minutes)
  full        - All tests (~75 minutes)

Examples:
  %(prog)s smoke                    # Quick smoke test
  %(prog)s full                     # Run everything
  %(prog)s strategy identity        # Run specific suites
  %(prog)s --coverage full          # Run with coverage
        """,
    )
    
    parser.add_argument(
        "suites",
        nargs="*",
        default=["smoke"],
        help="Test suites to run (default: smoke)",
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=1,
        help="Increase verbosity (can be used multiple times)",
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test suites and exit",
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("Available test suites:")
        print()
        for name, info in TEST_SUITES.items():
            print(f"  {name:12} - {info['description']} ({info['estimated_time']})")
        return 0
    
    return run_tests(args.suites, args.coverage, args.verbose)


if __name__ == "__main__":
    sys.exit(main())

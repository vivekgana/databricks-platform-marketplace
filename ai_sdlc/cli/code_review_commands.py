"""
CLI commands for PySpark code review.

Usage:
    python -m ai_sdlc.cli.code_review_commands review --files path/to/code.py
    python -m ai_sdlc.cli.code_review_commands review-pr 6340168
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from ai_sdlc.agents.code_review_agent import CodeReviewAgent
from ai_sdlc.evals.code_review_eval import CodeReviewEval


def review_files(
    files: List[str],
    work_item_id: Optional[str] = None,
    severity_threshold: str = "low",
    review_type: str = "all",
    output_dir: Optional[str] = None,
) -> int:
    """
    Review code files.

    Args:
        files: List of file paths to review
        work_item_id: Optional work item ID
        severity_threshold: Minimum severity to report
        review_type: Type of review (security, performance, logic, all)
        output_dir: Output directory for reports

    Returns:
        Exit code (0 = passed, 1 = failed)
    """
    # Initialize agent
    agent = CodeReviewAgent(
        work_item_id=work_item_id or "local",
        evidence_base_path=output_dir or "./code-review-results",
    )

    # Run review
    print(f"🔍 Reviewing {len(files)} files...")
    print(f"   Review type: {review_type}")
    print(f"   Severity threshold: {severity_threshold}")
    print()

    result = agent.execute(
        {
            "code_files": files,
            "severity_threshold": severity_threshold,
            "review_type": review_type,
        }
    )

    if not result["success"]:
        print(f"❌ Code review failed: {result.get('error_message')}")
        return 1

    data = result["data"]
    summary = data["summary"]

    # Print summary
    print("=" * 70)
    print(f"📊 Code Review Summary")
    print("=" * 70)
    print()
    print(f"Files reviewed:     {data['files_reviewed']}")
    print(f"Total findings:     {data['total_findings']}")
    print(f"Severity score:     {data['severity_score']} / 100")
    print()
    print("Findings by severity:")
    print(f"  🔴 Critical:      {summary['critical_count']}")
    print(f"  🟠 High:          {summary['high_count']}")
    print(f"  🟡 Medium:        {summary['medium_count']}")
    print(f"  🟢 Low:           {summary['low_count']}")
    print()

    # Run evaluator
    evaluator = CodeReviewEval(min_score=0.7)
    eval_result = evaluator.evaluate(result)

    print(f"Evaluation score:   {eval_result['score']:.2f}")
    print(
        f"Review status:      {'✅ PASSED' if eval_result['passed'] else '❌ FAILED'}"
    )
    print()

    # Print issues
    if eval_result["issues"]:
        print("Issues:")
        for issue in eval_result["issues"]:
            icon = (
                "🔴"
                if issue.severity == "critical"
                else "🟠" if issue.severity == "high" else "🟡"
            )
            blocking = " (BLOCKING)" if issue.blocking else ""
            print(f"  {icon} [{issue.category}] {issue.description}{blocking}")
        print()

    # Print recommendations
    if eval_result["recommendations"]:
        print("Recommendations:")
        for rec in eval_result["recommendations"]:
            print(f"  • {rec}")
        print()

    # Print report location
    if "report_file" in data:
        print(f"📄 Full report: {data['report_file']}")
        print()

    return 0 if eval_result["passed"] else 1


def review_pr(
    work_item_id: str,
    severity_threshold: str = "low",
    review_type: str = "all",
) -> int:
    """
    Review code for a PR.

    This finds all Python files modified in the work item's branch
    and runs code review on them.

    Args:
        work_item_id: Work item ID
        severity_threshold: Minimum severity to report
        review_type: Type of review (security, performance, logic, all)

    Returns:
        Exit code (0 = passed, 1 = failed)
    """
    print(f"🔍 Reviewing code for work item {work_item_id}...")
    print()

    # TODO: Integrate with git to find modified files
    # For now, find all Python files in current directory
    python_files = list(Path(".").rglob("*.py"))

    if not python_files:
        print("❌ No Python files found to review")
        return 1

    print(f"Found {len(python_files)} Python files")
    print()

    return review_files(
        files=[str(f) for f in python_files],
        work_item_id=work_item_id,
        severity_threshold=severity_threshold,
        review_type=review_type,
        output_dir=f"./.code-review/{work_item_id}",
    )


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PySpark Code Review CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review specific files
  python -m ai_sdlc.cli.code_review_commands review --files src/main.py src/utils.py

  # Review with severity threshold
  python -m ai_sdlc.cli.code_review_commands review --files src/*.py --severity high

  # Review only security issues
  python -m ai_sdlc.cli.code_review_commands review --files src/*.py --type security

  # Review PR code
  python -m ai_sdlc.cli.code_review_commands review-pr 6340168

  # Review PR with high severity threshold
  python -m ai_sdlc.cli.code_review_commands review-pr 6340168 --severity high
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Review command
    review_parser = subparsers.add_parser("review", help="Review code files")
    review_parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Files to review",
    )
    review_parser.add_argument(
        "--work-item-id",
        help="Work item ID (optional)",
    )
    review_parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        default="low",
        help="Minimum severity threshold (default: low)",
    )
    review_parser.add_argument(
        "--type",
        choices=["security", "performance", "logic", "all"],
        default="all",
        help="Type of review (default: all)",
    )
    review_parser.add_argument(
        "--output-dir",
        help="Output directory for reports (default: ./code-review-results)",
    )

    # Review PR command
    review_pr_parser = subparsers.add_parser("review-pr", help="Review code for PR")
    review_pr_parser.add_argument(
        "work_item_id",
        help="Work item ID",
    )
    review_pr_parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        default="low",
        help="Minimum severity threshold (default: low)",
    )
    review_pr_parser.add_argument(
        "--type",
        choices=["security", "performance", "logic", "all"],
        default="all",
        help="Type of review (default: all)",
    )

    args = parser.parse_args()

    if args.command == "review":
        exit_code = review_files(
            files=args.files,
            work_item_id=args.work_item_id,
            severity_threshold=args.severity,
            review_type=args.type,
            output_dir=args.output_dir,
        )
    elif args.command == "review-pr":
        exit_code = review_pr(
            work_item_id=args.work_item_id,
            severity_threshold=args.severity,
            review_type=args.type,
        )
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

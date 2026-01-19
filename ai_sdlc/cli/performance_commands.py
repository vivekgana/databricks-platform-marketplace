"""
CLI commands for Spark performance analysis.

Usage:
    python -m ai_sdlc.cli.performance_commands analyze-logs --log-path "dbfs:/path/to/eventlog" --work-item-id "12345"
    python -m ai_sdlc.cli.performance_commands analyze-query --query-plan-file "query_plan.txt" --work-item-id "12345"
    python -m ai_sdlc.cli.performance_commands analyze-metrics --metrics-file "metrics.json" --work-item-id "12345"
    python -m ai_sdlc.cli.performance_commands analyze-full --log-path "dbfs:/path/to/eventlog" --work-item-id "12345"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from ai_sdlc.agents.performance_analyzer_agent import PerformanceAnalyzerAgent


def analyze_logs(
    log_path: str,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
    skew_threshold: float = 3.0,
    spill_threshold_mb: int = 100,
) -> int:
    """Analyze Spark event logs for performance issues."""
    agent = PerformanceAnalyzerAgent(
        work_item_id=work_item_id or "local",
        config={},
        evidence_path=output_dir or "./performance-analysis",
    )

    print(f"🔍 Analyzing Spark event logs: {log_path}")
    print(f"   Skew threshold: {skew_threshold}x")
    print(f"   Spill threshold: {spill_threshold_mb}MB")
    print()

    result = agent.execute(
        {
            "analysis_type": "logs",
            "log_path": log_path,
            "thresholds": {
                "skew_threshold": skew_threshold,
                "spill_threshold_mb": spill_threshold_mb,
            },
        }
    )

    if not result["success"]:
        print(f"❌ Analysis failed: {result.get('error_message')}")
        return 1

    data = result["data"]

    # Print summary
    print("=" * 70)
    print("📊 Performance Analysis Summary")
    print("=" * 70)
    print()
    print(f"Performance Score: {data['performance_score']}/100")
    print(f"Issues Found:      {len(data['issues'])}")
    print(f"Bottlenecks:       {len(data['bottlenecks'])}")
    print()

    # Print issues by severity
    critical = [i for i in data["issues"] if i["severity"] == "critical"]
    high = [i for i in data["issues"] if i["severity"] == "high"]
    medium = [i for i in data["issues"] if i["severity"] == "medium"]
    low = [i for i in data["issues"] if i["severity"] == "low"]

    if critical:
        print(f"🔴 Critical Issues: {len(critical)}")
        for issue in critical[:3]:
            print(f"   • {issue['description']}")
    if high:
        print(f"🟠 High Severity:   {len(high)}")
        for issue in high[:3]:
            print(f"   • {issue['description']}")
    if medium:
        print(f"🟡 Medium Severity: {len(medium)}")
    if low:
        print(f"🟢 Low Severity:    {len(low)}")
    print()

    # Print top recommendations
    if data["recommendations"]:
        print("💡 Top Recommendations:")
        for rec in data["recommendations"][:5]:
            print(f"   • {rec}")
        print()

    # Print output files
    print(f"📄 Performance report:     {data['report_file']}")
    print(f"📄 Optimization script:    {data['optimization_script']}")
    print(f"📄 Metrics summary:        {data['metrics_summary']}")
    print()

    return 0


def analyze_query(
    query_plan_file: str,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
) -> int:
    """Analyze Spark query execution plan."""
    # Read query plan
    query_plan_path = Path(query_plan_file)
    if not query_plan_path.exists():
        print(f"❌ Query plan file not found: {query_plan_file}")
        return 1

    with open(query_plan_path, "r") as f:
        query_plan = f.read()

    agent = PerformanceAnalyzerAgent(
        work_item_id=work_item_id or "local",
        config={},
        evidence_path=output_dir or "./performance-analysis",
    )

    print(f"🔍 Analyzing query execution plan: {query_plan_file}")
    print()

    result = agent.execute(
        {
            "analysis_type": "query_plan",
            "query_plan": query_plan,
        }
    )

    if not result["success"]:
        print(f"❌ Analysis failed: {result.get('error_message')}")
        return 1

    data = result["data"]

    # Print summary
    print("=" * 70)
    print("📊 Query Plan Analysis Summary")
    print("=" * 70)
    print()
    print(f"Performance Score: {data['performance_score']}/100")
    print(f"Issues Found:      {len(data['issues'])}")
    print(f"Optimizations:     {len(data['recommendations'])}")
    print()

    # Print issues
    if data["issues"]:
        print("⚠️  Issues Detected:")
        for issue in data["issues"][:5]:
            print(f"   [{issue['severity'].upper()}] {issue['description']}")
            print(f"   💡 {issue['recommendation']}")
            print()

    # Print output files
    print(f"📄 Performance report:     {data['report_file']}")
    print(f"📄 Optimization script:    {data['optimization_script']}")
    print()

    return 0


def analyze_metrics(
    metrics_file: str,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
    response_time_threshold_ms: int = 2000,
    memory_threshold_gb: int = 10,
) -> int:
    """Analyze performance metrics."""
    # Read metrics
    metrics_path = Path(metrics_file)
    if not metrics_path.exists():
        print(f"❌ Metrics file not found: {metrics_file}")
        return 1

    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    agent = PerformanceAnalyzerAgent(
        work_item_id=work_item_id or "local",
        config={},
        evidence_path=output_dir or "./performance-analysis",
    )

    print(f"🔍 Analyzing performance metrics: {metrics_file}")
    print(f"   Response time threshold: {response_time_threshold_ms}ms")
    print(f"   Memory threshold: {memory_threshold_gb}GB")
    print()

    result = agent.execute(
        {
            "analysis_type": "metrics",
            "metrics": metrics,
            "thresholds": {
                "response_time_threshold_ms": response_time_threshold_ms,
                "memory_threshold_gb": memory_threshold_gb,
            },
        }
    )

    if not result["success"]:
        print(f"❌ Analysis failed: {result.get('error_message')}")
        return 1

    data = result["data"]

    # Print summary
    print("=" * 70)
    print("📊 Performance Metrics Summary")
    print("=" * 70)
    print()
    print(f"Performance Score: {data['performance_score']}/100")
    print(f"Issues Found:      {len(data['issues'])}")
    print()

    # Print key metrics
    if "metrics" in data:
        metrics_data = data["metrics"]
        print("📈 Key Metrics:")
        if "response_time_ms" in metrics_data:
            print(f"   Response Time: {metrics_data['response_time_ms']}ms")
        if "memory_usage_gb" in metrics_data:
            print(f"   Memory Usage:  {metrics_data['memory_usage_gb']:.2f}GB")
        if "cpu_usage_percent" in metrics_data:
            print(f"   CPU Usage:     {metrics_data['cpu_usage_percent']:.1f}%")
        print()

    # Print recommendations
    if data["recommendations"]:
        print("💡 Recommendations:")
        for rec in data["recommendations"]:
            print(f"   • {rec}")
        print()

    # Print output files
    print(f"📄 Performance report:     {data['report_file']}")
    print(f"📄 Metrics summary:        {data['metrics_summary']}")
    print()

    return 0


def analyze_full(
    log_path: str,
    work_item_id: Optional[str] = None,
    output_dir: Optional[str] = None,
    query_plan_file: Optional[str] = None,
    metrics_file: Optional[str] = None,
) -> int:
    """Perform comprehensive performance analysis."""
    agent = PerformanceAnalyzerAgent(
        work_item_id=work_item_id or "local",
        config={},
        evidence_path=output_dir or "./performance-analysis",
    )

    print(f"🔍 Performing comprehensive performance analysis")
    print(f"   Event logs:   {log_path}")
    if query_plan_file:
        print(f"   Query plan:   {query_plan_file}")
    if metrics_file:
        print(f"   Metrics:      {metrics_file}")
    print()

    # Prepare input data
    input_data = {
        "analysis_type": "full",
        "log_path": log_path,
    }

    # Add optional query plan
    if query_plan_file:
        query_plan_path = Path(query_plan_file)
        if query_plan_path.exists():
            with open(query_plan_path, "r") as f:
                input_data["query_plan"] = f.read()
        else:
            print(f"⚠️  Query plan file not found, skipping: {query_plan_file}")

    # Add optional metrics
    if metrics_file:
        metrics_path = Path(metrics_file)
        if metrics_path.exists():
            with open(metrics_path, "r") as f:
                input_data["metrics"] = json.load(f)
        else:
            print(f"⚠️  Metrics file not found, skipping: {metrics_file}")

    result = agent.execute(input_data)

    if not result["success"]:
        print(f"❌ Analysis failed: {result.get('error_message')}")
        return 1

    data = result["data"]

    # Print comprehensive summary
    print("=" * 70)
    print("📊 Comprehensive Performance Analysis")
    print("=" * 70)
    print()
    print(f"Overall Performance Score: {data['performance_score']}/100")
    print(f"Total Issues:              {len(data['issues'])}")
    print(f"Bottlenecks Identified:    {len(data['bottlenecks'])}")
    print()

    # Print issues by category
    categories = {}
    for issue in data["issues"]:
        cat = issue.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1

    if categories:
        print("📋 Issues by Category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat.replace('_', ' ').title()}: {count}")
        print()

    # Print top bottlenecks
    if data["bottlenecks"]:
        print("🚨 Top Bottlenecks:")
        for bottleneck in data["bottlenecks"][:5]:
            print(f"   • {bottleneck}")
        print()

    # Print top recommendations
    if data["recommendations"]:
        print("💡 Top Recommendations:")
        for rec in data["recommendations"][:5]:
            print(f"   • {rec}")
        print()

    # Print output files
    print("=" * 70)
    print("📄 Generated Files:")
    print("=" * 70)
    print(f"Performance Report:      {data['report_file']}")
    print(f"Optimization Script:     {data['optimization_script']}")
    print(f"Metrics Summary:         {data['metrics_summary']}")
    print()

    # Print next steps
    print("Next steps:")
    print("1. Review the performance report for detailed analysis")
    print("2. Apply recommended optimizations from the optimization script")
    print("3. Test changes and re-run analysis to measure improvements")
    print("4. Monitor metrics over time to track performance trends")
    print()

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Spark Performance Analysis CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Spark event logs
  python -m ai_sdlc.cli.performance_commands analyze-logs \\
    --log-path "dbfs:/databricks/eventlogs/app-123/eventlog" \\
    --work-item-id "12345"

  # Analyze query execution plan
  python -m ai_sdlc.cli.performance_commands analyze-query \\
    --query-plan-file "query_plan.txt" \\
    --work-item-id "12345"

  # Analyze performance metrics
  python -m ai_sdlc.cli.performance_commands analyze-metrics \\
    --metrics-file "metrics.json" \\
    --work-item-id "12345" \\
    --response-time-threshold-ms 1000

  # Comprehensive analysis
  python -m ai_sdlc.cli.performance_commands analyze-full \\
    --log-path "dbfs:/databricks/eventlogs/app-123/eventlog" \\
    --query-plan-file "query_plan.txt" \\
    --metrics-file "metrics.json" \\
    --work-item-id "12345"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Analyze logs command
    logs_parser = subparsers.add_parser("analyze-logs", help="Analyze Spark event logs")
    logs_parser.add_argument(
        "--log-path", required=True, help="Path to Spark event log"
    )
    logs_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    logs_parser.add_argument(
        "--output-dir", help="Output directory (default: ./performance-analysis)"
    )
    logs_parser.add_argument(
        "--skew-threshold",
        type=float,
        default=3.0,
        help="Data skew threshold multiplier (default: 3.0)",
    )
    logs_parser.add_argument(
        "--spill-threshold-mb",
        type=int,
        default=100,
        help="Spill to disk threshold in MB (default: 100)",
    )

    # Analyze query command
    query_parser = subparsers.add_parser(
        "analyze-query", help="Analyze query execution plan"
    )
    query_parser.add_argument(
        "--query-plan-file", required=True, help="Path to query plan text file"
    )
    query_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    query_parser.add_argument(
        "--output-dir", help="Output directory (default: ./performance-analysis)"
    )

    # Analyze metrics command
    metrics_parser = subparsers.add_parser(
        "analyze-metrics", help="Analyze performance metrics"
    )
    metrics_parser.add_argument(
        "--metrics-file", required=True, help="Path to metrics JSON file"
    )
    metrics_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    metrics_parser.add_argument(
        "--output-dir", help="Output directory (default: ./performance-analysis)"
    )
    metrics_parser.add_argument(
        "--response-time-threshold-ms",
        type=int,
        default=2000,
        help="Response time threshold in ms (default: 2000)",
    )
    metrics_parser.add_argument(
        "--memory-threshold-gb",
        type=int,
        default=10,
        help="Memory usage threshold in GB (default: 10)",
    )

    # Analyze full command
    full_parser = subparsers.add_parser(
        "analyze-full", help="Comprehensive performance analysis"
    )
    full_parser.add_argument(
        "--log-path", required=True, help="Path to Spark event log"
    )
    full_parser.add_argument("--work-item-id", help="Work item ID (optional)")
    full_parser.add_argument(
        "--output-dir", help="Output directory (default: ./performance-analysis)"
    )
    full_parser.add_argument(
        "--query-plan-file", help="Path to query plan text file (optional)"
    )
    full_parser.add_argument(
        "--metrics-file", help="Path to metrics JSON file (optional)"
    )

    args = parser.parse_args()

    if args.command == "analyze-logs":
        exit_code = analyze_logs(
            log_path=args.log_path,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
            skew_threshold=args.skew_threshold,
            spill_threshold_mb=args.spill_threshold_mb,
        )
    elif args.command == "analyze-query":
        exit_code = analyze_query(
            query_plan_file=args.query_plan_file,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
        )
    elif args.command == "analyze-metrics":
        exit_code = analyze_metrics(
            metrics_file=args.metrics_file,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
            response_time_threshold_ms=args.response_time_threshold_ms,
            memory_threshold_gb=args.memory_threshold_gb,
        )
    elif args.command == "analyze-full":
        exit_code = analyze_full(
            log_path=args.log_path,
            work_item_id=args.work_item_id,
            output_dir=args.output_dir,
            query_plan_file=args.query_plan_file,
            metrics_file=args.metrics_file,
        )
    else:
        parser.print_help()
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

"""
Performance Analyzer Agent

Analyzes Spark logs, query plans, and performance metrics to identify
bottlenecks and provide optimization recommendations.

Features:
- Spark UI log parsing
- Query plan analysis (physical and logical plans)
- Performance bottleneck detection
- Resource utilization analysis
- Cost optimization recommendations
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_agent import BaseAgent


class PerformanceAnalyzerAgent(BaseAgent):
    """
    Agent for analyzing Spark performance and identifying optimization opportunities.

    Analyzes:
    - Spark event logs
    - Query execution plans
    - Stage and task metrics
    - Resource utilization
    - Data skew and shuffle patterns
    """

    # Performance issue patterns
    PERFORMANCE_PATTERNS = {
        "data_skew": {
            "pattern": r"max_task_duration.*?(\d+).*?median_task_duration.*?(\d+)",
            "threshold": 3.0,  # Max/median ratio
            "severity": "high",
            "description": "Data skew detected - tasks have uneven execution times",
            "recommendation": "Use salting, repartitioning, or broadcast joins",
        },
        "spill_to_disk": {
            "pattern": r"spill.*?disk",
            "severity": "high",
            "description": "Spill to disk detected - insufficient memory",
            "recommendation": "Increase executor memory or reduce shuffle partition size",
        },
        "excessive_shuffle": {
            "pattern": r"shuffle.*?write.*?(\d+(?:\.\d+)?)\s*([MGT]B)",
            "threshold": 10.0,  # GB
            "severity": "medium",
            "description": "Excessive shuffle detected",
            "recommendation": "Consider broadcast joins or reduce shuffle operations",
        },
        "small_files": {
            "pattern": r"(\d+)\s+files.*?total.*?(\d+(?:\.\d+)?)\s*([MGT]B)",
            "threshold": 128,  # MB per file
            "severity": "medium",
            "description": "Small file problem detected",
            "recommendation": "Use OPTIMIZE or coalesce to reduce file count",
        },
        "cartesian_product": {
            "pattern": r"CartesianProduct",
            "severity": "critical",
            "description": "Cartesian product detected in query plan",
            "recommendation": "Add join conditions to avoid cross joins",
        },
        "missing_predicate_pushdown": {
            "pattern": r"Filter.*?after.*?Scan",
            "severity": "medium",
            "description": "Filter not pushed down to data source",
            "recommendation": "Ensure filters are applied before expensive operations",
        },
        "broadcast_join_threshold": {
            "pattern": r"BroadcastHashJoin.*?(\d+(?:\.\d+)?)\s*([MGT]B)",
            "threshold": 10.0,  # MB
            "severity": "low",
            "description": "Large broadcast join detected",
            "recommendation": "Consider SortMergeJoin for large datasets",
        },
    }

    # Optimization recommendations by category
    OPTIMIZATION_CATEGORIES = {
        "memory": {
            "name": "Memory Optimization",
            "checks": [
                "executor_memory_usage",
                "driver_memory_usage",
                "spill_to_disk",
                "cache_usage",
            ],
        },
        "shuffle": {
            "name": "Shuffle Optimization",
            "checks": [
                "shuffle_read_bytes",
                "shuffle_write_bytes",
                "shuffle_partitions",
                "data_skew",
            ],
        },
        "io": {
            "name": "I/O Optimization",
            "checks": ["small_files", "file_format", "compression", "partitioning"],
        },
        "compute": {
            "name": "Compute Optimization",
            "checks": ["parallelism", "task_duration", "cpu_utilization", "gc_time"],
        },
        "query": {
            "name": "Query Optimization",
            "checks": [
                "predicate_pushdown",
                "broadcast_joins",
                "cartesian_products",
                "expensive_operations",
            ],
        },
    }

    def execute(
        self, input_data: Dict[str, Any], timeout_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Analyze Spark performance from logs and metrics.

        Args:
            input_data: Dictionary with:
                - analysis_type: Type of analysis (logs, query_plan, metrics, full)
                - spark_event_log: Path to Spark event log file
                - query_plan: Query execution plan (physical or logical)
                - metrics: Performance metrics dictionary
                - job_id: Optional Databricks job ID
                - threshold: Performance threshold (slow, medium, fast)

        Returns:
            Result dictionary with performance analysis and recommendations
        """
        self._log_start()

        try:
            analysis_type = input_data.get("analysis_type")
            if not analysis_type:
                return self._create_result(
                    success=False,
                    error_message="Missing required parameter: analysis_type",
                )

            # Accept both parameter names for backward compatibility
            spark_event_log = input_data.get("spark_event_log") or input_data.get(
                "log_path"
            )
            query_plan = input_data.get("query_plan")
            metrics = input_data.get("metrics", {})
            thresholds = input_data.get("thresholds", {})
            job_id = input_data.get("job_id")
            threshold = input_data.get("threshold", "medium")

            # Validate required inputs based on analysis type
            if analysis_type == "logs" and not spark_event_log:
                return self._create_result(
                    success=False,
                    error_message="Missing required parameter for logs analysis: log_path",
                )
            if analysis_type == "query_plan" and not query_plan:
                return self._create_result(
                    success=False,
                    error_message="Missing required parameter for query plan analysis: query_plan",
                )
            if analysis_type == "metrics" and not metrics:
                return self._create_result(
                    success=False,
                    error_message="Missing required parameter for metrics analysis: metrics",
                )
            if analysis_type == "full" and not (
                spark_event_log or query_plan or metrics
            ):
                return self._create_result(
                    success=False,
                    error_message="Full analysis requires at least one of: log_path, query_plan, metrics",
                )

            results = {}
            issues = []
            recommendations = []
            evidence_paths = []

            # Analyze Spark event logs
            if analysis_type in ["logs", "full"] and spark_event_log:
                log_result = self._analyze_event_log(spark_event_log)
                results["log_analysis"] = log_result
                issues.extend(log_result["issues"])
                recommendations.extend(log_result["recommendations"])

            # Analyze query execution plan
            if analysis_type in ["query_plan", "full"] and query_plan:
                plan_result = self._analyze_query_plan(query_plan)
                results["query_plan_analysis"] = plan_result
                issues.extend(plan_result["issues"])
                recommendations.extend(plan_result["recommendations"])

            # Analyze performance metrics
            if analysis_type in ["metrics", "full"] and metrics:
                metrics_result = self._analyze_metrics(metrics, threshold)
                results["metrics_analysis"] = metrics_result
                issues.extend(metrics_result["issues"])
                recommendations.extend(metrics_result["recommendations"])

            # Categorize issues by severity
            categorized_issues = self._categorize_issues(issues)

            # Generate performance score
            performance_score = self._calculate_performance_score(
                categorized_issues, metrics
            )

            # Generate comprehensive report
            report = self._generate_performance_report(
                results, categorized_issues, performance_score, recommendations
            )
            report_file = self._save_evidence_file("performance-report.md", report)
            evidence_paths.append(report_file)

            # Generate optimization script
            optimization_script = self._generate_optimization_script(recommendations)
            script_file = self._save_evidence_file(
                "optimization-script.py", optimization_script
            )
            evidence_paths.append(script_file)

            # Save metrics summary
            summary = {
                "analysis_type": analysis_type,
                "performance_score": performance_score,
                "total_issues": len(issues),
                "critical_issues": categorized_issues["critical"],
                "high_issues": categorized_issues["high"],
                "medium_issues": categorized_issues["medium"],
                "low_issues": categorized_issues["low"],
                "recommendations": recommendations,
                "issues": issues,
            }

            summary_file = self._save_evidence_file(
                "performance-summary.json", json.dumps(summary, indent=2)
            )
            evidence_paths.append(summary_file)

            self._log_complete(True)

            return self._create_result(
                success=True,
                data={
                    "analysis_type": analysis_type,
                    "performance_score": performance_score,
                    "total_issues": len(issues),
                    "categorized_issues": categorized_issues,
                    "recommendations_count": len(recommendations),
                    "report_file": report_file,
                    "script_file": script_file,
                },
                evidence_paths=evidence_paths,
            )

        except Exception as e:
            self.logger.error(f"Error during performance analysis: {e}")
            return self._create_result(
                success=False,
                error_message=f"Performance analysis failed: {e}",
            )

    def _analyze_event_log(self, log_path: str) -> Dict[str, Any]:
        """Analyze Spark event log for performance issues."""
        issues = []
        recommendations = []
        metrics = {}

        try:
            # Read log file
            with open(log_path, "r") as f:
                log_content = f.read()

            # Extract key metrics
            metrics = self._extract_log_metrics(log_content)

            # Check for performance patterns
            for pattern_name, pattern_info in self.PERFORMANCE_PATTERNS.items():
                matches = re.finditer(
                    pattern_info["pattern"], log_content, re.IGNORECASE
                )

                for match in matches:
                    # Check threshold if applicable
                    if "threshold" in pattern_info:
                        # Extract numeric values from match
                        values = [float(g) for g in match.groups() if g]
                        if values and self._exceeds_threshold(
                            values, pattern_info["threshold"]
                        ):
                            issues.append(
                                {
                                    "type": pattern_name,
                                    "severity": pattern_info["severity"],
                                    "description": pattern_info["description"],
                                    "location": f"Line {log_content[:match.start()].count(chr(10)) + 1}",
                                }
                            )
                            recommendations.append(pattern_info["recommendation"])
                    else:
                        issues.append(
                            {
                                "type": pattern_name,
                                "severity": pattern_info["severity"],
                                "description": pattern_info["description"],
                                "location": f"Line {log_content[:match.start()].count(chr(10)) + 1}",
                            }
                        )
                        recommendations.append(pattern_info["recommendation"])

        except FileNotFoundError:
            self.logger.warning(f"Event log file not found: {log_path}")
        except Exception as e:
            self.logger.error(f"Error analyzing event log: {e}")

        return {
            "metrics": metrics,
            "issues": issues,
            "recommendations": list(set(recommendations)),  # Remove duplicates
        }

    def _extract_log_metrics(self, log_content: str) -> Dict[str, Any]:
        """Extract key metrics from Spark event log."""
        metrics = {}

        # Extract job duration
        job_duration_match = re.search(
            r"Job\s+\d+\s+finished.*?took\s+([\d.]+)\s*s", log_content
        )
        if job_duration_match:
            metrics["job_duration_seconds"] = float(job_duration_match.group(1))

        # Extract shuffle metrics
        shuffle_read_match = re.search(
            r"shuffle read:\s*([\d.]+)\s*([KMGT]?B)", log_content, re.IGNORECASE
        )
        if shuffle_read_match:
            metrics["shuffle_read_bytes"] = self._parse_size(
                shuffle_read_match.group(1), shuffle_read_match.group(2)
            )

        shuffle_write_match = re.search(
            r"shuffle write:\s*([\d.]+)\s*([KMGT]?B)", log_content, re.IGNORECASE
        )
        if shuffle_write_match:
            metrics["shuffle_write_bytes"] = self._parse_size(
                shuffle_write_match.group(1), shuffle_write_match.group(2)
            )

        # Extract GC time
        gc_time_match = re.search(r"GC time:\s*([\d.]+)\s*ms", log_content)
        if gc_time_match:
            metrics["gc_time_ms"] = float(gc_time_match.group(1))

        return metrics

    def _parse_size(self, value: str, unit: str) -> int:
        """Parse size string to bytes."""
        multipliers = {
            "B": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
        }
        return int(float(value) * multipliers.get(unit.upper(), 1))

    def _exceeds_threshold(self, values: List[float], threshold: float) -> bool:
        """Check if values exceed threshold."""
        if len(values) >= 2:
            # For skew detection: max/median ratio
            return values[0] / values[1] > threshold
        elif len(values) == 1:
            # For absolute threshold
            return values[0] > threshold
        return False

    def _analyze_query_plan(self, query_plan: str) -> Dict[str, Any]:
        """Analyze Spark query execution plan."""
        issues = []
        recommendations = []

        # Check for expensive operations
        if "CartesianProduct" in query_plan:
            issues.append(
                {
                    "type": "cartesian_product",
                    "severity": "critical",
                    "description": "Cartesian product detected - will generate N×M rows",
                    "location": "Query plan",
                }
            )
            recommendations.append("Add join condition to avoid cartesian product")

        if "Sort" in query_plan and "Exchange" in query_plan:
            issues.append(
                {
                    "type": "sort_after_shuffle",
                    "severity": "medium",
                    "description": "Sort operation after shuffle - expensive",
                    "location": "Query plan",
                }
            )
            recommendations.append(
                "Consider using sortWithinPartitions instead of sort"
            )

        # Check for missing optimizations
        if re.search(r"Filter.*?\n.*?Scan", query_plan):
            issues.append(
                {
                    "type": "filter_not_pushed",
                    "severity": "medium",
                    "description": "Filter not pushed down to scan",
                    "location": "Query plan",
                }
            )
            recommendations.append("Ensure predicate pushdown is enabled")

        # Check broadcast join size
        broadcast_match = re.search(
            r"BroadcastHashJoin.*?\[([\d.]+)\s*([KMGT]?B)", query_plan
        )
        if broadcast_match:
            size_bytes = self._parse_size(
                broadcast_match.group(1), broadcast_match.group(2)
            )
            if size_bytes > 10 * 1024 * 1024:  # 10 MB
                issues.append(
                    {
                        "type": "large_broadcast",
                        "severity": "low",
                        "description": f"Large broadcast join ({broadcast_match.group(1)} {broadcast_match.group(2)})",
                        "location": "Query plan",
                    }
                )
                recommendations.append(
                    "Consider using SortMergeJoin for large datasets"
                )

        return {"issues": issues, "recommendations": list(set(recommendations))}

    def _analyze_metrics(
        self, metrics: Dict[str, Any], threshold: str
    ) -> Dict[str, Any]:
        """Analyze performance metrics."""
        issues = []
        recommendations = []

        # Define thresholds
        thresholds = {
            "fast": {"duration": 10, "memory": 0.5, "cpu": 0.6},
            "medium": {"duration": 60, "memory": 0.7, "cpu": 0.8},
            "slow": {"duration": 300, "memory": 0.85, "cpu": 0.9},
        }

        limits = thresholds.get(threshold, thresholds["medium"])

        # Check job duration
        duration = metrics.get("duration_seconds", 0)
        if duration > limits["duration"]:
            issues.append(
                {
                    "type": "slow_job",
                    "severity": (
                        "high" if duration > limits["duration"] * 2 else "medium"
                    ),
                    "description": f"Job took {duration}s (threshold: {limits['duration']}s)",
                    "location": "Overall performance",
                }
            )
            recommendations.append("Optimize query plan and increase parallelism")

        # Check memory usage
        memory_usage = metrics.get("memory_usage_percent", 0)
        if memory_usage > limits["memory"]:
            issues.append(
                {
                    "type": "high_memory",
                    "severity": "high",
                    "description": f"Memory usage at {memory_usage*100:.1f}%",
                    "location": "Resource utilization",
                }
            )
            recommendations.append(
                "Increase executor memory or reduce data processing per partition"
            )

        # Check CPU utilization
        cpu_usage = metrics.get("cpu_usage_percent", 0)
        if cpu_usage < 0.3:
            issues.append(
                {
                    "type": "low_cpu",
                    "severity": "medium",
                    "description": f"Low CPU utilization ({cpu_usage*100:.1f}%)",
                    "location": "Resource utilization",
                }
            )
            recommendations.append("Increase parallelism or reduce shuffle operations")

        # Check data skew
        task_duration_max = metrics.get("max_task_duration_ms", 0)
        task_duration_median = metrics.get("median_task_duration_ms", 1)
        if task_duration_max / task_duration_median > 3:
            issues.append(
                {
                    "type": "data_skew",
                    "severity": "high",
                    "description": f"Data skew detected (max/median ratio: {task_duration_max/task_duration_median:.1f})",
                    "location": "Task execution",
                }
            )
            recommendations.append("Use salting or custom partitioning to balance data")

        return {"issues": issues, "recommendations": list(set(recommendations))}

    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize issues by severity."""
        categorized = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for issue in issues:
            severity = issue.get("severity", "low")
            if severity in categorized:
                categorized[severity] += 1

        return categorized

    def _calculate_performance_score(
        self, categorized_issues: Dict[str, int], metrics: Dict[str, Any]
    ) -> float:
        """Calculate overall performance score (0-100)."""
        # Start with perfect score
        score = 100.0

        # Deduct points for issues
        score -= categorized_issues["critical"] * 20
        score -= categorized_issues["high"] * 10
        score -= categorized_issues["medium"] * 5
        score -= categorized_issues["low"] * 2

        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))

    def _generate_performance_report(
        self,
        results: Dict[str, Any],
        categorized_issues: Dict[str, int],
        performance_score: float,
        recommendations: List[str],
    ) -> str:
        """Generate comprehensive performance report."""
        doc = f"""# Spark Performance Analysis Report

**Work Item ID:** {self.work_item_id}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Performance Score:** {performance_score:.1f}/100

---

## Executive Summary

"""

        # Performance rating
        if performance_score >= 90:
            rating = "Excellent ✅"
            summary = "Performance is optimal with minimal issues detected."
        elif performance_score >= 75:
            rating = "Good ✓"
            summary = "Performance is acceptable with some room for improvement."
        elif performance_score >= 50:
            rating = "Fair ⚠️"
            summary = "Performance needs improvement. Several issues detected."
        else:
            rating = "Poor ❌"
            summary = "Performance is poor. Immediate optimization required."

        doc += f"""
**Rating:** {rating}
**Summary:** {summary}

### Issues by Severity

| Severity | Count |
|----------|-------|
| 🔴 Critical | {categorized_issues['critical']} |
| 🟠 High | {categorized_issues['high']} |
| 🟡 Medium | {categorized_issues['medium']} |
| 🟢 Low | {categorized_issues['low']} |

---

## Detailed Analysis

"""

        # Log analysis
        if "log_analysis" in results:
            log_result = results["log_analysis"]
            doc += f"""
### Event Log Analysis

**Metrics Extracted:**
"""
            for metric, value in log_result.get("metrics", {}).items():
                doc += f"- {metric}: {value}\n"

            if log_result.get("issues"):
                doc += "\n**Issues Found:**\n"
                for issue in log_result["issues"]:
                    severity_icon = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(issue["severity"], "⚪")
                    doc += f"- {severity_icon} [{issue['type']}] {issue['description']} ({issue['location']})\n"

        # Query plan analysis
        if "query_plan_analysis" in results:
            plan_result = results["query_plan_analysis"]
            doc += """
### Query Plan Analysis

"""
            if plan_result.get("issues"):
                doc += "**Issues Found:**\n"
                for issue in plan_result["issues"]:
                    severity_icon = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(issue["severity"], "⚪")
                    doc += (
                        f"- {severity_icon} [{issue['type']}] {issue['description']}\n"
                    )

        # Metrics analysis
        if "metrics_analysis" in results:
            metrics_result = results["metrics_analysis"]
            doc += """
### Performance Metrics Analysis

"""
            if metrics_result.get("issues"):
                doc += "**Issues Found:**\n"
                for issue in metrics_result["issues"]:
                    severity_icon = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(issue["severity"], "⚪")
                    doc += (
                        f"- {severity_icon} [{issue['type']}] {issue['description']}\n"
                    )

        doc += """
---

## Optimization Recommendations

"""

        # Group recommendations by category
        categorized_recs = self._categorize_recommendations(recommendations)

        for category, recs in categorized_recs.items():
            if recs:
                doc += f"\n### {category}\n\n"
                for rec in recs:
                    doc += f"- {rec}\n"

        doc += """
---

## Action Plan

### Priority 1: Critical Issues
1. Fix all cartesian products in queries
2. Address data skew immediately
3. Resolve memory spill to disk

### Priority 2: High-Impact Optimizations
1. Enable predicate pushdown
2. Optimize shuffle operations
3. Increase parallelism where needed

### Priority 3: General Improvements
1. Enable auto-optimization for Delta tables
2. Review and adjust Spark configurations
3. Monitor resource utilization continuously

---

## Spark Configuration Recommendations

```python
# Recommended Spark configurations
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128 MB
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
```

---

**Generated by:** AI-SDLC Performance Analyzer Agent
"""

        return doc

    def _categorize_recommendations(
        self, recommendations: List[str]
    ) -> Dict[str, List[str]]:
        """Categorize recommendations by optimization type."""
        categories = {
            "Memory Optimization": [],
            "Shuffle Optimization": [],
            "Query Optimization": [],
            "I/O Optimization": [],
            "Resource Optimization": [],
        }

        memory_keywords = ["memory", "cache", "spill", "heap"]
        shuffle_keywords = ["shuffle", "partition", "skew", "broadcast"]
        query_keywords = ["query", "join", "filter", "predicate", "plan"]
        io_keywords = ["file", "read", "write", "optimize", "compact"]
        resource_keywords = ["cpu", "executor", "parallelism", "core"]

        for rec in recommendations:
            rec_lower = rec.lower()
            if any(kw in rec_lower for kw in memory_keywords):
                categories["Memory Optimization"].append(rec)
            elif any(kw in rec_lower for kw in shuffle_keywords):
                categories["Shuffle Optimization"].append(rec)
            elif any(kw in rec_lower for kw in query_keywords):
                categories["Query Optimization"].append(rec)
            elif any(kw in rec_lower for kw in io_keywords):
                categories["I/O Optimization"].append(rec)
            elif any(kw in rec_lower for kw in resource_keywords):
                categories["Resource Optimization"].append(rec)
            else:
                categories["Query Optimization"].append(rec)  # Default

        return categories

    def _generate_optimization_script(self, recommendations: List[str]) -> str:
        """Generate Python script with optimization code."""
        script = '''"""
Spark Performance Optimization Script

Generated based on performance analysis recommendations.
"""

from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("performance-optimization").getOrCreate()

# Configure Spark for optimal performance
def configure_spark_optimizations():
    """Apply recommended Spark configurations."""

    # Adaptive Query Execution
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
    spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
    spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")

    # Shuffle optimizations
    spark.conf.set("spark.sql.shuffle.partitions", "200")  # Adjust based on data size
    spark.conf.set("spark.sql.files.maxPartitionBytes", "134217728")  # 128 MB

    # Delta Lake optimizations
    spark.conf.set("spark.databricks.delta.optimizeWrite.enabled", "true")
    spark.conf.set("spark.databricks.delta.autoCompact.enabled", "true")
    spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite", "true")
    spark.conf.set("spark.databricks.delta.properties.defaults.autoOptimize.autoCompact", "true")

    # Memory optimizations
    spark.conf.set("spark.memory.fraction", "0.8")
    spark.conf.set("spark.memory.storageFraction", "0.3")

    # I/O optimizations
    spark.conf.set("spark.sql.parquet.compression.codec", "snappy")
    spark.conf.set("spark.sql.files.openCostInBytes", "134217728")  # 128 MB

    print("✅ Spark optimizations configured")


def optimize_delta_table(table_name, zorder_columns=None):
    """
    Optimize Delta table for better query performance.

    Args:
        table_name: Full table name (catalog.schema.table)
        zorder_columns: List of columns to Z-order by
    """
    print(f"Optimizing table: {table_name}")

    # Compact small files
    spark.sql(f"OPTIMIZE {table_name}")

    # Z-order for frequently filtered columns
    if zorder_columns:
        zorder_cols = ", ".join(zorder_columns)
        spark.sql(f"OPTIMIZE {table_name} ZORDER BY ({zorder_cols})")

    # Enable auto-optimization
    spark.sql(f"""
        ALTER TABLE {table_name} SET TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
    """)

    print(f"✅ Table optimized: {table_name}")


def analyze_data_skew(df, partition_column):
    """
    Analyze data distribution for skew detection.

    Args:
        df: DataFrame to analyze
        partition_column: Column to check for skew
    """
    print(f"Analyzing data skew on column: {partition_column}")

    distribution = df.groupBy(partition_column).count().orderBy("count", ascending=False)
    distribution.show(20)

    # Get statistics
    stats = distribution.agg(
        {"count": "max", "count": "min", "count": "avg"}
    ).collect()[0]

    max_count = stats["max(count)"]
    min_count = stats["min(count)"]
    avg_count = stats["avg(count)"]

    skew_ratio = max_count / avg_count if avg_count > 0 else 0

    print(f"Skew ratio (max/avg): {skew_ratio:.2f}")

    if skew_ratio > 3:
        print("⚠️  High data skew detected!")
        print("Consider using salting or custom partitioning")
    else:
        print("✅ Data distribution is balanced")

    return skew_ratio


def apply_salting(df, partition_column, salt_count=10):
    """
    Apply salting to reduce data skew.

    Args:
        df: DataFrame with skewed data
        partition_column: Skewed column
        salt_count: Number of salt values
    """
    from pyspark.sql.functions import col, concat, lit, rand

    # Add salt column
    df_salted = df.withColumn(
        "salted_key",
        concat(col(partition_column), lit("_"), (rand() * salt_count).cast("int"))
    )

    return df_salted


# Example usage
if __name__ == "__main__":
    # Configure optimizations
    configure_spark_optimizations()

    # Example: Optimize a table
    # optimize_delta_table("prod.sales.transactions", zorder_columns=["date", "customer_id"])

    # Example: Analyze data skew
    # df = spark.table("prod.sales.transactions")
    # analyze_data_skew(df, "customer_id")

    print("\\n✅ Optimization script completed")
'''

        return script

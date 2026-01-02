#!/usr/bin/env python3
"""
Spark Profiler MCP Server

A Model Context Protocol server that provides Spark query performance analysis,
optimization suggestions, and execution plan visualization.

This server runs as a stdio MCP server and provides tools for:
- Query plan analysis
- Performance profiling
- Bottleneck identification
- Optimization recommendations
- Cost estimation
"""

import json
import sys
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('spark-profiler-mcp.log')]
)
logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a Spark query execution"""
    query_id: str
    duration_ms: int
    stages: int
    tasks: int
    shuffle_read_bytes: int
    shuffle_write_bytes: int
    input_bytes: int
    output_bytes: int
    peak_memory_bytes: int
    spilled_bytes: int


@dataclass
class OptimizationSuggestion:
    """Optimization suggestion for Spark query"""
    category: str  # performance, cost, reliability
    severity: str  # critical, warning, info
    title: str
    description: str
    code_example: Optional[str] = None
    estimated_improvement: Optional[str] = None


@dataclass
class PlanNode:
    """Node in Spark execution plan"""
    node_id: int
    node_type: str
    description: str
    children: List['PlanNode']
    metrics: Dict[str, Any]
    cost_estimate: Optional[float] = None


class SparkProfiler:
    """Analyzes Spark query plans and provides optimization suggestions"""

    def __init__(self):
        self.shuffle_threshold_mb = 100
        self.spill_threshold_mb = 10

    def analyze_plan(self, plan_text: str) -> Dict[str, Any]:
        """
        Analyze a Spark execution plan

        Args:
            plan_text: Text representation of Spark plan (from explain())

        Returns:
            Analysis results with suggestions
        """
        suggestions = []

        # Check for expensive operations
        if 'Exchange' in plan_text or 'Shuffle' in plan_text:
            shuffle_count = plan_text.count('Exchange')
            if shuffle_count > 3:
                suggestions.append(OptimizationSuggestion(
                    category='performance',
                    severity='warning',
                    title=f'Multiple shuffles detected ({shuffle_count})',
                    description='Query contains multiple shuffle operations which can be expensive',
                    code_example='''
# Consider reducing shuffles by:
# 1. Using broadcast joins for small tables
df_large.join(broadcast(df_small), "key")

# 2. Repartitioning once at the beginning
df = df.repartition(200, "partition_key")

# 3. Using coalesce instead of repartition for reducing partitions
df = df.coalesce(10)
''',
                    estimated_improvement='20-50% performance improvement'
                ))

        # Check for broadcast potential
        if 'Join' in plan_text and 'BroadcastHashJoin' not in plan_text:
            suggestions.append(OptimizationSuggestion(
                category='performance',
                severity='info',
                title='Join operation without broadcast',
                description='Consider broadcasting small tables to avoid shuffle',
                code_example='''
from pyspark.sql.functions import broadcast

# Broadcast small lookup tables
df_result = df_large.join(
    broadcast(df_small),
    on="key",
    how="left"
)
''',
                estimated_improvement='30-70% for joins with small tables'
            ))

        # Check for sort operations
        if 'Sort' in plan_text:
            suggestions.append(OptimizationSuggestion(
                category='performance',
                severity='info',
                title='Sort operation detected',
                description='Sorts can be expensive, especially on large datasets',
                code_example='''
# If sort is not needed, remove ORDER BY clauses
# If needed for windowing, consider using DISTRIBUTE BY + SORT BY

df.repartition("partition_col").sortWithinPartitions("sort_col")
''',
                estimated_improvement='10-30% if sort can be optimized or removed'
            ))

        # Check for UDFs
        if 'UDF' in plan_text or 'pythonUDF' in plan_text:
            suggestions.append(OptimizationSuggestion(
                category='performance',
                severity='warning',
                title='Python UDF detected',
                description='Python UDFs prevent optimizations and are slower than native functions',
                code_example='''
# Replace Python UDFs with:
# 1. Built-in Spark functions
from pyspark.sql import functions as F
df.withColumn("result", F.upper(F.col("name")))

# 2. Pandas UDFs (vectorized)
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("double")
def vectorized_func(s: pd.Series) -> pd.Series:
    return s * 2

df.withColumn("doubled", vectorized_func("value"))
''',
                estimated_improvement='5-10x performance improvement'
            ))

        # Check for full table scans
        if 'FileScan' in plan_text and 'PushedFilters' not in plan_text:
            suggestions.append(OptimizationSuggestion(
                category='performance',
                severity='warning',
                title='Full table scan without predicate pushdown',
                description='Query is scanning entire table without pushed filters',
                code_example='''
# Ensure partition pruning and predicate pushdown:

# 1. Partition tables by frequently filtered columns
df.write.partitionBy("date", "region").format("delta").save(path)

# 2. Use filters early in the query
df = spark.read.format("delta").load(path) \\
    .filter(F.col("date") >= "2024-01-01")  # Push filter early

# 3. Use Z-ORDER for Delta tables
spark.sql("OPTIMIZE table_name ZORDER BY (frequently_filtered_col)")
''',
                estimated_improvement='50-90% for filtered queries'
            ))

        # Check for Cartesian products
        if 'CartesianProduct' in plan_text:
            suggestions.append(OptimizationSuggestion(
                category='performance',
                severity='critical',
                title='Cartesian product detected',
                description='Cartesian products can explode data size and cause OOM',
                code_example='''
# Replace Cartesian product with explicit join condition:

# Bad:
df1.crossJoin(df2)

# Good:
df1.join(df2, on="join_key", how="inner")
''',
                estimated_improvement='Required to avoid failures'
            ))

        return {
            'plan_summary': {
                'has_shuffles': 'Exchange' in plan_text,
                'has_broadcasts': 'Broadcast' in plan_text,
                'has_sorts': 'Sort' in plan_text,
                'has_udfs': 'UDF' in plan_text or 'pythonUDF' in plan_text,
                'join_count': plan_text.count('Join'),
                'shuffle_count': plan_text.count('Exchange')
            },
            'suggestions': [asdict(s) for s in suggestions],
            'overall_score': self._calculate_score(suggestions)
        }

    def analyze_metrics(self, metrics: QueryMetrics) -> Dict[str, Any]:
        """
        Analyze query execution metrics

        Args:
            metrics: Query execution metrics

        Returns:
            Analysis with suggestions
        """
        suggestions = []

        # Check shuffle size
        shuffle_mb = metrics.shuffle_read_bytes / (1024 * 1024)
        if shuffle_mb > self.shuffle_threshold_mb:
            suggestions.append(OptimizationSuggestion(
                category='performance',
                severity='warning',
                title=f'Large shuffle size: {shuffle_mb:.1f} MB',
                description='Consider reducing shuffle by repartitioning or broadcasting',
                estimated_improvement='20-40% reduction in shuffle time'
            ))

        # Check spill
        spill_mb = metrics.spilled_bytes / (1024 * 1024)
        if spill_mb > self.spill_threshold_mb:
            suggestions.append(OptimizationSuggestion(
                category='performance',
                severity='critical',
                title=f'Disk spill detected: {spill_mb:.1f} MB',
                description='Insufficient memory causing disk spill',
                code_example='''
# Increase executor memory or reduce partition count:

spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.sql.shuffle.partitions", "200")

# Or increase memory fraction:
spark.conf.set("spark.memory.fraction", "0.8")
''',
                estimated_improvement='2-5x performance improvement'
            ))

        # Check task imbalance
        if metrics.stages > 0:
            avg_tasks_per_stage = metrics.tasks / metrics.stages
            if avg_tasks_per_stage < 10:
                suggestions.append(OptimizationSuggestion(
                    category='performance',
                    severity='info',
                    title='Low task count may indicate under-parallelization',
                    description=f'Average {avg_tasks_per_stage:.0f} tasks per stage',
                    code_example='''
# Increase parallelism:
df = df.repartition(200)  # Or appropriate number based on data size

# Or configure shuffle partitions:
spark.conf.set("spark.sql.shuffle.partitions", "200")
'''
                ))

        return {
            'metrics_summary': asdict(metrics),
            'suggestions': [asdict(s) for s in suggestions],
            'health_score': self._calculate_score(suggestions)
        }

    def estimate_cost(self, metrics: QueryMetrics,
                     dbu_cost_per_hour: float = 0.15) -> Dict[str, Any]:
        """
        Estimate cost of query execution

        Args:
            metrics: Query execution metrics
            dbu_cost_per_hour: Cost per DBU hour

        Returns:
            Cost estimation
        """
        # Simple cost model based on duration and data processed
        duration_hours = metrics.duration_ms / (1000 * 60 * 60)

        # Estimate DBUs based on data size (simplified)
        data_tb = (metrics.input_bytes + metrics.shuffle_read_bytes) / (1024**4)
        estimated_dbus = max(1, data_tb * 10)  # Rough estimate

        cost = duration_hours * estimated_dbus * dbu_cost_per_hour

        return {
            'estimated_cost_usd': round(cost, 4),
            'duration_hours': round(duration_hours, 4),
            'estimated_dbus': round(estimated_dbus, 2),
            'data_processed_tb': round(data_tb, 3),
            'breakdown': {
                'compute': round(cost * 0.7, 4),
                'storage_io': round(cost * 0.2, 4),
                'shuffle': round(cost * 0.1, 4)
            }
        }

    def _calculate_score(self, suggestions: List[OptimizationSuggestion]) -> int:
        """Calculate health score (0-100) based on suggestions"""
        score = 100
        for suggestion in suggestions:
            if suggestion.severity == 'critical':
                score -= 25
            elif suggestion.severity == 'warning':
                score -= 10
            elif suggestion.severity == 'info':
                score -= 5
        return max(0, score)


class MCPServer:
    """MCP Server implementation for Spark Profiler"""

    def __init__(self):
        self.profiler = SparkProfiler()
        self.tools = {
            'analyze_plan': self.analyze_plan,
            'analyze_metrics': self.analyze_metrics,
            'estimate_cost': self.estimate_cost,
            'get_optimization_tips': self.get_optimization_tips
        }

    def analyze_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: Analyze Spark execution plan"""
        plan_text = params.get('plan_text', '')
        return self.profiler.analyze_plan(plan_text)

    def analyze_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: Analyze query execution metrics"""
        metrics = QueryMetrics(**params.get('metrics', {}))
        return self.profiler.analyze_metrics(metrics)

    def estimate_cost(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: Estimate query cost"""
        metrics = QueryMetrics(**params.get('metrics', {}))
        dbu_cost = params.get('dbu_cost_per_hour', 0.15)
        return self.profiler.estimate_cost(metrics, dbu_cost)

    def get_optimization_tips(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Tool: Get general optimization tips"""
        category = params.get('category', 'all')

        tips = {
            'performance': [
                'Use broadcast joins for small tables (< 10MB)',
                'Partition large tables by frequently filtered columns',
                'Cache frequently accessed DataFrames',
                'Use columnar formats like Delta Lake or Parquet',
                'Avoid Python UDFs, prefer built-in functions',
                'Use Z-ORDER for Delta tables on filter columns'
            ],
            'cost': [
                'Use spot instances for non-critical workloads',
                'Right-size cluster configuration',
                'Use auto-scaling clusters',
                'Optimize file sizes (128MB - 1GB)',
                'Enable auto-optimization for Delta tables',
                'Use serverless SQL warehouses for BI queries'
            ],
            'reliability': [
                'Implement idempotent pipelines',
                'Use Delta MERGE for upserts',
                'Enable checkpointing for streaming',
                'Implement retry logic with exponential backoff',
                'Monitor data quality with expectations',
                'Use transaction logs for audit trails'
            ]
        }

        if category == 'all':
            return {'tips': tips}
        else:
            return {'tips': {category: tips.get(category, [])}}

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        method = request.get('method')
        params = request.get('params', {})

        if method == 'tools/list':
            return {
                'tools': [
                    {
                        'name': 'analyze_plan',
                        'description': 'Analyze Spark execution plan and provide optimization suggestions',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'plan_text': {
                                    'type': 'string',
                                    'description': 'Spark execution plan text from explain()'
                                }
                            },
                            'required': ['plan_text']
                        }
                    },
                    {
                        'name': 'analyze_metrics',
                        'description': 'Analyze query execution metrics',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'metrics': {
                                    'type': 'object',
                                    'description': 'Query execution metrics'
                                }
                            },
                            'required': ['metrics']
                        }
                    },
                    {
                        'name': 'estimate_cost',
                        'description': 'Estimate cost of query execution',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'metrics': {'type': 'object'},
                                'dbu_cost_per_hour': {'type': 'number'}
                            }
                        }
                    },
                    {
                        'name': 'get_optimization_tips',
                        'description': 'Get general optimization tips by category',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'category': {
                                    'type': 'string',
                                    'enum': ['performance', 'cost', 'reliability', 'all']
                                }
                            }
                        }
                    }
                ]
            }

        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_params = params.get('arguments', {})

            if tool_name in self.tools:
                try:
                    result = self.tools[tool_name](tool_params)
                    return {'content': [{'type': 'text', 'text': json.dumps(result, indent=2)}]}
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    return {'error': str(e)}
            else:
                return {'error': f'Unknown tool: {tool_name}'}

        else:
            return {'error': f'Unknown method: {method}'}

    def run(self):
        """Run MCP server (stdio)"""
        logger.info("Spark Profiler MCP Server starting...")

        for line in sys.stdin:
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                error_response = {'error': str(e)}
                print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    server = MCPServer()
    server.run()

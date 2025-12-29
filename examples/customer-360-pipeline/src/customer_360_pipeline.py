"""
Customer 360 Pipeline Example
=============================

This example demonstrates building a complete Customer 360 data product using
the Databricks Engineering Plugin with medallion architecture.

Architecture:
- Bronze: Raw customer data from multiple sources
- Silver: Cleansed and standardized customer data
- Gold: Customer 360 aggregated view

Data Sources:
- CRM data (Salesforce)
- Transaction history
- Customer support tickets
- Web analytics
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import DeltaTable
from datetime import datetime
import sys


class Customer360Pipeline:
    """Customer 360 data pipeline with medallion architecture."""
    
    def __init__(self, spark: SparkSession, catalog: str, schema: str):
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.bronze_schema = f"{catalog}.bronze"
        self.silver_schema = f"{catalog}.silver"
        self.gold_schema = f"{catalog}.gold"
    
    def run(self, execution_date: str = None):
        """Execute the complete pipeline."""
        if not execution_date:
            execution_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"Starting Customer 360 pipeline for {execution_date}")
        
        # Bronze layer - ingest raw data
        self.ingest_crm_data(execution_date)
        self.ingest_transactions(execution_date)
        self.ingest_support_tickets(execution_date)
        
        # Silver layer - cleanse and standardize
        self.process_customer_silver()
        self.process_transactions_silver()
        self.process_support_silver()
        
        # Gold layer - create Customer 360
        self.create_customer_360()
        
        # Data quality checks
        self.run_quality_checks()
        
        print(f"Pipeline completed successfully for {execution_date}")
    
    def ingest_crm_data(self, execution_date: str):
        """Ingest raw CRM data to Bronze layer."""
        print("Ingesting CRM data...")
        
        # Read from source (example: S3, Salesforce, etc.)
        source_path = f"s3://data-lake/raw/crm/{execution_date}/"
        
        df = (self.spark.read
            .format("json")
            .load(source_path)
            .withColumn("_ingested_at", current_timestamp())
            .withColumn("_source_file", input_file_name())
            .withColumn("_execution_date", lit(execution_date))
        )
        
        # Write to Bronze
        (df.write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .saveAsTable(f"{self.bronze_schema}.crm_customers")
        )
        
        print(f"Ingested {df.count()} CRM records")
    
    def ingest_transactions(self, execution_date: str):
        """Ingest transaction data to Bronze layer."""
        print("Ingesting transaction data...")
        
        source_path = f"s3://data-lake/raw/transactions/{execution_date}/"
        
        df = (self.spark.read
            .format("parquet")
            .load(source_path)
            .withColumn("_ingested_at", current_timestamp())
            .withColumn("_execution_date", lit(execution_date))
        )
        
        (df.write
            .format("delta")
            .mode("append")
            .partitionBy("transaction_date")
            .saveAsTable(f"{self.bronze_schema}.transactions")
        )
        
        print(f"Ingested {df.count()} transaction records")
    
    def ingest_support_tickets(self, execution_date: str):
        """Ingest support ticket data to Bronze layer."""
        print("Ingesting support tickets...")
        
        source_path = f"s3://data-lake/raw/support/{execution_date}/"
        
        df = (self.spark.read
            .format("json")
            .load(source_path)
            .withColumn("_ingested_at", current_timestamp())
            .withColumn("_execution_date", lit(execution_date))
        )
        
        (df.write
            .format("delta")
            .mode("append")
            .saveAsTable(f"{self.bronze_schema}.support_tickets")
        )
        
        print(f"Ingested {df.count()} support ticket records")
    
    def process_customer_silver(self):
        """Process and cleanse customer data for Silver layer."""
        print("Processing customer Silver layer...")
        
        # Read from Bronze
        bronze_df = self.spark.read.table(f"{self.bronze_schema}.crm_customers")
        
        # Cleanse and standardize
        silver_df = (bronze_df
            # Deduplicate
            .dropDuplicates(["customer_id"])
            
            # Standardize email
            .withColumn("email", lower(trim(col("email"))))
            
            # Validate and clean phone numbers
            .withColumn("phone", 
                regexp_replace(col("phone"), r"[^0-9]", ""))
            
            # Standardize address
            .withColumn("address_standardized",
                struct(
                    upper(trim(col("address.street"))).alias("street"),
                    upper(trim(col("address.city"))).alias("city"),
                    upper(trim(col("address.state"))).alias("state"),
                    trim(col("address.zip")).alias("zip"),
                    upper(trim(col("address.country"))).alias("country")
                ))
            
            # Add data quality flags
            .withColumn("has_valid_email",
                col("email").rlike(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
            .withColumn("has_valid_phone",
                length(col("phone")).between(10, 15))
            
            # Add metadata
            .withColumn("processed_at", current_timestamp())
            .withColumn("data_quality_score",
                when(col("has_valid_email") & col("has_valid_phone"), lit(1.0))
                .when(col("has_valid_email") | col("has_valid_phone"), lit(0.7))
                .otherwise(lit(0.3))
            )
        )
        
        # Write to Silver (SCD Type 1)
        (silver_df.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(f"{self.silver_schema}.customers")
        )
        
        print(f"Processed {silver_df.count()} customer records to Silver")
    
    def process_transactions_silver(self):
        """Process transactions for Silver layer."""
        print("Processing transactions Silver layer...")
        
        bronze_df = self.spark.read.table(f"{self.bronze_schema}.transactions")
        
        silver_df = (bronze_df
            # Filter out cancelled transactions
            .filter(col("status") != "cancelled")
            
            # Standardize amounts
            .withColumn("amount_usd",
                when(col("currency") == "USD", col("amount"))
                .otherwise(col("amount") * col("exchange_rate_to_usd"))
            )
            
            # Add derived fields
            .withColumn("transaction_year", year(col("transaction_date")))
            .withColumn("transaction_month", month(col("transaction_date")))
            .withColumn("transaction_quarter", quarter(col("transaction_date")))
            
            # Add metadata
            .withColumn("processed_at", current_timestamp())
        )
        
        (silver_df.write
            .format("delta")
            .mode("overwrite")
            .partitionBy("transaction_year", "transaction_month")
            .saveAsTable(f"{self.silver_schema}.transactions")
        )
        
        print(f"Processed {silver_df.count()} transactions to Silver")
    
    def process_support_silver(self):
        """Process support tickets for Silver layer."""
        print("Processing support tickets Silver layer...")
        
        bronze_df = self.spark.read.table(f"{self.bronze_schema}.support_tickets")
        
        silver_df = (bronze_df
            # Categorize tickets
            .withColumn("priority_score",
                when(col("priority") == "critical", lit(4))
                .when(col("priority") == "high", lit(3))
                .when(col("priority") == "medium", lit(2))
                .otherwise(lit(1))
            )
            
            # Calculate resolution time
            .withColumn("resolution_hours",
                when(col("resolved_at").isNotNull(),
                    (unix_timestamp(col("resolved_at")) - 
                     unix_timestamp(col("created_at"))) / 3600
                )
            )
            
            # Add metadata
            .withColumn("processed_at", current_timestamp())
        )
        
        (silver_df.write
            .format("delta")
            .mode("overwrite")
            .saveAsTable(f"{self.silver_schema}.support_tickets")
        )
        
        print(f"Processed {silver_df.count()} support tickets to Silver")
    
    def create_customer_360(self):
        """Create Customer 360 Gold aggregation."""
        print("Creating Customer 360 Gold view...")
        
        # Read Silver tables
        customers = self.spark.read.table(f"{self.silver_schema}.customers")
        transactions = self.spark.read.table(f"{self.silver_schema}.transactions")
        support = self.spark.read.table(f"{self.silver_schema}.support_tickets")
        
        # Aggregate transactions by customer
        transaction_agg = (transactions
            .groupBy("customer_id")
            .agg(
                count("*").alias("total_transactions"),
                sum("amount_usd").alias("lifetime_value"),
                avg("amount_usd").alias("avg_transaction_value"),
                max("transaction_date").alias("last_transaction_date"),
                min("transaction_date").alias("first_transaction_date")
            )
        )
        
        # Aggregate support tickets by customer
        support_agg = (support
            .groupBy("customer_id")
            .agg(
                count("*").alias("total_support_tickets"),
                avg("priority_score").alias("avg_ticket_priority"),
                avg("resolution_hours").alias("avg_resolution_hours"),
                max("created_at").alias("last_support_ticket_date")
            )
        )
        
        # Create Customer 360
        customer_360 = (customers
            .join(transaction_agg, "customer_id", "left")
            .join(support_agg, "customer_id", "left")
            
            # Fill nulls for customers with no transactions/tickets
            .fillna({
                "total_transactions": 0,
                "lifetime_value": 0.0,
                "total_support_tickets": 0
            })
            
            # Calculate customer segment
            .withColumn("customer_segment",
                when(col("lifetime_value") >= 10000, lit("platinum"))
                .when(col("lifetime_value") >= 5000, lit("gold"))
                .when(col("lifetime_value") >= 1000, lit("silver"))
                .otherwise(lit("bronze"))
            )
            
            # Calculate customer health score
            .withColumn("health_score",
                (col("data_quality_score") * 0.2 +
                 least(col("total_transactions") / 100, lit(1.0)) * 0.3 +
                 (1 - least(coalesce(col("total_support_tickets"), lit(0)) / 10, lit(1.0))) * 0.3 +
                 least(datediff(current_date(), col("last_transaction_date")) / 365, lit(1.0)) * 0.2
                )
            )
            
            # Add metadata
            .withColumn("created_at", current_timestamp())
            .withColumn("updated_at", current_timestamp())
        )
        
        # Write to Gold (full refresh)
        (customer_360.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(f"{self.gold_schema}.customer_360")
        )
        
        print(f"Created Customer 360 with {customer_360.count()} records")
        
        # Optimize table
        self.spark.sql(f"""
            OPTIMIZE {self.gold_schema}.customer_360
            ZORDER BY (customer_segment, lifetime_value)
        """)
        
        print("Optimized Customer 360 table")
    
    def run_quality_checks(self):
        """Run data quality checks on Customer 360."""
        print("Running data quality checks...")
        
        customer_360 = self.spark.read.table(f"{self.gold_schema}.customer_360")
        
        checks = {
            "no_duplicate_customers": customer_360.count() == customer_360.select("customer_id").distinct().count(),
            "no_null_customer_ids": customer_360.filter(col("customer_id").isNull()).count() == 0,
            "valid_email_format": customer_360.filter(~col("has_valid_email")).count() == 0,
            "positive_lifetime_value": customer_360.filter(col("lifetime_value") < 0).count() == 0,
            "valid_segments": customer_360.filter(
                ~col("customer_segment").isin(["bronze", "silver", "gold", "platinum"])
            ).count() == 0
        }
        
        all_passed = all(checks.values())
        
        for check_name, passed in checks.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"  {check_name}: {status}")
        
        if not all_passed:
            raise Exception("Quality checks failed!")
        
        print("All quality checks passed!")


def main():
    """Main entry point for pipeline execution."""
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("Customer360Pipeline") \
        .getOrCreate()
    
    # Get parameters
    catalog = spark.conf.get("spark.databricks.catalog", "dev_catalog")
    schema = spark.conf.get("spark.databricks.schema", "customer_data")
    execution_date = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run pipeline
    pipeline = Customer360Pipeline(spark, catalog, schema)
    pipeline.run(execution_date)
    
    spark.stop()


if __name__ == "__main__":
    main()

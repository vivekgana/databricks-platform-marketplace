# Databricks notebook source
# MAGIC %md
# MAGIC # Data Exploration for ML Project
# MAGIC
# MAGIC This notebook explores the data for customer churn prediction.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Import Libraries

# COMMAND ----------

from pyspark.sql import functions as F
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data

# COMMAND ----------

# Load customer data
customers_df = spark.table("main.bronze.customers")
transactions_df = spark.table("main.bronze.transactions")

display(customers_df.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Quality Checks

# COMMAND ----------

print(f"Customers count: {customers_df.count()}")
print(f"Transactions count: {transactions_df.count()}")

# Check for nulls
customers_df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in customers_df.columns]).show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Distribution Analysis

# COMMAND ----------

# Analyze churn distribution
churn_dist = customers_df.groupBy("churn").count().toPandas()

plt.figure(figsize=(8, 6))
sns.barplot(data=churn_dist, x="churn", y="count")
plt.title("Churn Distribution")
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Correlation Analysis

# COMMAND ----------

# Calculate correlations
pandas_df = customers_df.select(
    "total_spend", "total_transactions", "days_since_last_transaction", "churn"
).toPandas()

correlation_matrix = pandas_df.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
plt.title("Feature Correlations")
plt.show()

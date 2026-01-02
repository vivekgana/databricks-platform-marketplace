---
name: data-classification
description: Data classification strategies, tagging frameworks, sensitivity levels, and automated classification patterns for Unity Catalog.
triggers:
  - data classification
  - data tagging
  - sensitivity levels
  - pii classification
category: classification
---

# Data Classification Skill

## Overview

Comprehensive data classification framework for identifying, tagging, and managing data based on sensitivity, regulatory requirements, and business context.

## Classification Framework

### Sensitivity Levels
- **PUBLIC**: Approved for public disclosure
- **INTERNAL**: Internal business use only
- **CONFIDENTIAL**: Sensitive business data
- **RESTRICTED**: Highly sensitive regulated data (PII, PHI, PCI)

### Data Domains
- **CUSTOMER**: Customer and prospect data
- **FINANCIAL**: Financial and accounting data
- **EMPLOYEE**: HR and employee information
- **PRODUCT**: Product and service data
- **OPERATIONAL**: System and operational data

### PII Categories
- **DIRECT_IDENTIFIERS**: Name, email, SSN, phone
- **QUASI_IDENTIFIERS**: Zip code, DOB, gender
- **SENSITIVE_ATTRIBUTES**: Health, race, religion, biometrics
- **FINANCIAL_DATA**: Credit cards, bank accounts, salary

## Classification Methods

### 1. Schema-Based Classification
```python
def classify_by_schema(column_name: str, data_type: str) -> dict:
    """Classify based on column name and type."""
    classification = {"sensitivity": "INTERNAL"}

    col_lower = column_name.lower()

    if any(x in col_lower for x in ['ssn', 'social_security', 'tax_id']):
        classification = {"sensitivity": "RESTRICTED", "pii": "DIRECT_IDENTIFIERS"}
    elif any(x in col_lower for x in ['email', 'phone', 'address']):
        classification = {"sensitivity": "CONFIDENTIAL", "pii": "DIRECT_IDENTIFIERS"}
    elif any(x in col_lower for x in ['salary', 'credit_card', 'bank_account']):
        classification = {"sensitivity": "RESTRICTED", "pii": "FINANCIAL_DATA"}

    return classification
```

### 2. Content-Based Classification
```python
def classify_by_content(table: str, column: str, sample_rate: float = 0.01):
    """Sample data content for classification."""
    samples = spark.table(table).sample(sample_rate).select(column).limit(100)

    pii_patterns = {
        'SSN': r'\b\d{3}-?\d{2}-?\d{4}\b',
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'CREDIT_CARD': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'PHONE': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    }

    detected_pii = []
    for row in samples.collect():
        value = str(row[0])
        for pii_type, pattern in pii_patterns.items():
            if re.match(pattern, value):
                detected_pii.append(pii_type)

    return list(set(detected_pii))
```

### 3. Tag Application
```sql
-- Create classification tags
CREATE TAG governance.sensitivity;
CREATE TAG governance.data_domain;
CREATE TAG governance.pii_category;

-- Apply to catalog
ALTER CATALOG production
SET TAGS ('governance.data_domain' = 'CUSTOMER');

-- Apply to table
ALTER TABLE production.customers.profiles
SET TAGS (
  'governance.sensitivity' = 'RESTRICTED',
  'governance.pii_category' = 'DIRECT_IDENTIFIERS'
);

-- Apply to column
ALTER TABLE production.customers.profiles
ALTER COLUMN email SET TAGS ('governance.sensitivity' = 'CONFIDENTIAL');
```

## Automated Classification

```python
class DataClassifier:
    def __init__(self):
        self.classification_rules = self.load_rules()

    def classify_catalog(self, catalog: str):
        """Auto-classify entire catalog."""
        schemas = list_schemas(catalog)
        for schema in schemas:
            tables = list_tables(catalog, schema)
            for table in tables:
                self.classify_table(f"{catalog}.{schema}.{table}")

    def classify_table(self, table_name: str):
        """Classify table and columns."""
        table_info = get_table_info(table_name)

        # Table-level classification
        table_class = self.infer_table_classification(table_info)
        self.apply_table_tags(table_name, table_class)

        # Column-level classification
        for column in table_info.columns:
            column_class = self.classify_column(column)
            self.apply_column_tags(table_name, column.name, column_class)

    def classify_column(self, column) -> dict:
        """Classify individual column."""
        # Schema-based
        schema_class = classify_by_schema(column.name, column.type)

        # Content-based (if high confidence not achieved)
        if schema_class["sensitivity"] == "INTERNAL":
            content_class = classify_by_content(table, column.name)
            if content_class:
                return content_class

        return schema_class
```

## Best Practices

1. **Start with High-Value Data**: Classify PII and regulated data first
2. **Automate Where Possible**: Use rules and ML for consistency
3. **Human Validation**: Review automated classifications
4. **Document Rationale**: Maintain classification decisions
5. **Regular Re-classification**: Update when schemas change
6. **Align with Policies**: Link classification to access/retention policies

## Templates

- **classification-rules.yaml**: Classification rule definitions
- **tag-taxonomy.sql**: Tag schema and values
- **classification-workflow.py**: Automated classification pipeline

## Examples

- **pii-classification**: PII detection and tagging
- **sensitivity-assignment**: Sensitivity level classification
- **compliance-mapping**: Map classifications to regulations

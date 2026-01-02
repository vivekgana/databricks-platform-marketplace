# Setup Data Classification Command

## Description
Configure comprehensive data classification framework with automated tagging, sensitivity levels, and metadata standards for Unity Catalog assets.

## Usage
```bash
claude /databricks-governance:setup-data-classification [options]
```

## Examples

### Initialize Classification Framework
```bash
claude /databricks-governance:setup-data-classification --init
```

### Classify Specific Catalog
```bash
claude /databricks-governance:setup-data-classification \
  --catalog production \
  --auto-classify
```

### Apply Custom Classification Rules
```bash
claude /databricks-governance:setup-data-classification \
  --catalog production \
  --rules-file ./classification-rules.yaml \
  --dry-run
```

### Scan and Tag PII
```bash
claude /databricks-governance:setup-data-classification \
  --catalog production \
  --tag-pii \
  --sensitivity high
```

## What It Does

1. **Classification Framework Setup**
   - Creates classification taxonomy
   - Defines sensitivity levels (Public, Internal, Confidential, Restricted)
   - Establishes data domains (Customer, Financial, Operational, Product)
   - Sets up metadata tags and standards

2. **Automated Classification**
   - Scans table schemas and column names
   - Applies ML-based content analysis
   - Identifies PII, PHI, PCI patterns
   - Tags based on classification rules

3. **Tag Management**
   - Creates Unity Catalog tags
   - Applies tags to catalogs, schemas, tables, columns
   - Manages tag inheritance
   - Tracks tag propagation

4. **Policy Association**
   - Links classifications to access policies
   - Maps sensitivity to retention policies
   - Associates encryption requirements
   - Defines masking rules by classification

5. **Documentation**
   - Generates data catalog documentation
   - Creates classification guide
   - Exports data dictionary
   - Maintains audit trail

## Classification Framework

### Sensitivity Levels

```yaml
sensitivity_levels:
  PUBLIC:
    description: "Data approved for public disclosure"
    retention: 7 years
    encryption: optional
    access: unrestricted
    examples:
      - Product catalogs
      - Marketing materials
      - Public reports

  INTERNAL:
    description: "Internal business data"
    retention: 5 years
    encryption: at_rest
    access: employee_only
    examples:
      - Internal reports
      - Operational metrics
      - Project documents

  CONFIDENTIAL:
    description: "Sensitive business data"
    retention: 7 years
    encryption: at_rest_and_transit
    access: need_to_know
    examples:
      - Customer contact info
      - Financial summaries
      - Strategic plans

  RESTRICTED:
    description: "Highly sensitive regulated data"
    retention: 10 years
    encryption: at_rest_and_transit_with_cmek
    access: explicit_grant_only
    masking: required
    examples:
      - SSN, credit cards
      - Medical records (PHI)
      - Payment data (PCI)
```

### Data Domains

```yaml
data_domains:
  CUSTOMER:
    description: "Customer and prospect data"
    owner: customer_data_team
    steward: privacy_officer
    regulations:
      - GDPR
      - CCPA
    default_sensitivity: CONFIDENTIAL

  FINANCIAL:
    description: "Financial and accounting data"
    owner: finance_team
    steward: cfo
    regulations:
      - SOX
      - PCI-DSS
    default_sensitivity: RESTRICTED

  EMPLOYEE:
    description: "Employee and HR data"
    owner: hr_team
    steward: hr_director
    regulations:
      - GDPR (EU employees)
      - Various labor laws
    default_sensitivity: RESTRICTED

  PRODUCT:
    description: "Product and service data"
    owner: product_team
    steward: product_manager
    default_sensitivity: INTERNAL

  OPERATIONAL:
    description: "System and operational data"
    owner: engineering_team
    steward: data_platform_lead
    default_sensitivity: INTERNAL
```

### PII Categories

```yaml
pii_categories:
  DIRECT_IDENTIFIERS:
    patterns:
      - full_name
      - email_address
      - phone_number
      - ssn
      - passport_number
      - drivers_license
    sensitivity: RESTRICTED
    masking: full_redaction

  QUASI_IDENTIFIERS:
    patterns:
      - zip_code
      - date_of_birth
      - gender
      - city
      - employer
    sensitivity: CONFIDENTIAL
    masking: partial_redaction

  SENSITIVE_ATTRIBUTES:
    patterns:
      - health_condition
      - racial_origin
      - religious_belief
      - political_opinion
      - sexual_orientation
    sensitivity: RESTRICTED
    masking: full_redaction

  FINANCIAL_DATA:
    patterns:
      - credit_card_number
      - bank_account_number
      - salary
      - financial_transaction
    sensitivity: RESTRICTED
    masking: tokenization
```

## Classification Rules

### Pattern-Based Rules
```python
classification_rules = {
    # Email patterns
    "email": {
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "sensitivity": "CONFIDENTIAL",
        "pii_category": "DIRECT_IDENTIFIERS",
        "tags": ["PII", "CONTACT_INFO"]
    },

    # SSN patterns
    "ssn": {
        "pattern": r"^\d{3}-\d{2}-\d{4}$",
        "sensitivity": "RESTRICTED",
        "pii_category": "DIRECT_IDENTIFIERS",
        "tags": ["PII", "SSN", "HIGHLY_SENSITIVE"],
        "masking": "full_redaction"
    },

    # Credit card patterns
    "credit_card": {
        "pattern": r"^\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}$",
        "sensitivity": "RESTRICTED",
        "pii_category": "FINANCIAL_DATA",
        "tags": ["PCI", "PAYMENT_DATA"],
        "masking": "tokenization"
    },

    # Phone patterns
    "phone": {
        "pattern": r"^\+?1?\d{9,15}$",
        "sensitivity": "CONFIDENTIAL",
        "pii_category": "DIRECT_IDENTIFIERS",
        "tags": ["PII", "CONTACT_INFO"]
    }
}
```

### Column Name Heuristics
```python
column_classification = {
    # High confidence patterns
    "email": "CONFIDENTIAL",
    "ssn": "RESTRICTED",
    "credit_card": "RESTRICTED",
    "password": "RESTRICTED",
    "secret": "RESTRICTED",
    "salary": "RESTRICTED",

    # Medium confidence patterns
    "phone": "CONFIDENTIAL",
    "address": "CONFIDENTIAL",
    "dob": "CONFIDENTIAL",
    "birth_date": "CONFIDENTIAL",

    # Low sensitivity
    "product_id": "INTERNAL",
    "category": "INTERNAL",
    "description": "INTERNAL"
}
```

## Implementation

### Step 1: Create Classification Tags
```sql
-- Create sensitivity tags
CREATE TAG IF NOT EXISTS governance.tags.sensitivity;
CREATE TAG IF NOT EXISTS governance.tags.data_domain;
CREATE TAG IF NOT EXISTS governance.tags.pii_category;
CREATE TAG IF NOT EXISTS governance.tags.retention_period;
CREATE TAG IF NOT EXISTS governance.tags.data_owner;

-- Create tag values
ALTER TAG governance.tags.sensitivity SET VALUES
  ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED');

ALTER TAG governance.tags.data_domain SET VALUES
  ('CUSTOMER', 'FINANCIAL', 'EMPLOYEE', 'PRODUCT', 'OPERATIONAL');

ALTER TAG governance.tags.pii_category SET VALUES
  ('DIRECT_IDENTIFIERS', 'QUASI_IDENTIFIERS', 'SENSITIVE_ATTRIBUTES', 'FINANCIAL_DATA');
```

### Step 2: Apply Classification
```sql
-- Classify catalog
ALTER CATALOG production
  SET TAGS (
    'governance.tags.sensitivity' = 'CONFIDENTIAL',
    'governance.tags.data_domain' = 'CUSTOMER'
  );

-- Classify schema
ALTER SCHEMA production.customers
  SET TAGS (
    'governance.tags.sensitivity' = 'RESTRICTED',
    'governance.tags.data_domain' = 'CUSTOMER',
    'governance.tags.data_owner' = 'customer_data_team'
  );

-- Classify table
ALTER TABLE production.customers.profiles
  SET TAGS (
    'governance.tags.sensitivity' = 'RESTRICTED',
    'governance.tags.pii_category' = 'DIRECT_IDENTIFIERS',
    'governance.tags.retention_period' = '7_years'
  );

-- Classify column
ALTER TABLE production.customers.profiles
  ALTER COLUMN email
  SET TAGS (
    'governance.tags.sensitivity' = 'RESTRICTED',
    'governance.tags.pii_category' = 'DIRECT_IDENTIFIERS'
  );
```

### Step 3: Automated Classification Script
```python
from databricks.sdk import WorkspaceClient
from typing import Dict, List
import re

class DataClassifier:
    def __init__(self):
        self.w = WorkspaceClient()
        self.classification_rules = self.load_rules()

    def classify_catalog(self, catalog_name: str):
        """Classify all tables in a catalog."""
        schemas = self.w.schemas.list(catalog_name=catalog_name)

        for schema in schemas:
            tables = self.w.tables.list(
                catalog_name=catalog_name,
                schema_name=schema.name
            )

            for table in tables:
                self.classify_table(
                    catalog_name,
                    schema.name,
                    table.name
                )

    def classify_table(self, catalog: str, schema: str, table: str):
        """Classify table and columns."""
        full_name = f"{catalog}.{schema}.{table}"
        table_info = self.w.tables.get(full_name)

        # Analyze table classification
        table_classification = self.analyze_table(table_info)

        # Apply table tags
        self.apply_table_tags(full_name, table_classification)

        # Classify each column
        for column in table_info.columns:
            column_classification = self.classify_column(column)
            self.apply_column_tags(
                full_name,
                column.name,
                column_classification
            )

    def classify_column(self, column) -> Dict[str, str]:
        """Classify a column based on name and type."""
        classification = {
            "sensitivity": "INTERNAL",
            "pii_category": None,
            "tags": []
        }

        col_name_lower = column.name.lower()

        # Check for PII patterns
        if any(pattern in col_name_lower for pattern in
               ['email', 'mail']):
            classification["sensitivity"] = "CONFIDENTIAL"
            classification["pii_category"] = "DIRECT_IDENTIFIERS"
            classification["tags"].append("PII")

        elif any(pattern in col_name_lower for pattern in
                ['ssn', 'social_security', 'tax_id']):
            classification["sensitivity"] = "RESTRICTED"
            classification["pii_category"] = "DIRECT_IDENTIFIERS"
            classification["tags"].extend(["PII", "SSN"])

        elif any(pattern in col_name_lower for pattern in
                ['credit_card', 'card_number', 'cvv']):
            classification["sensitivity"] = "RESTRICTED"
            classification["pii_category"] = "FINANCIAL_DATA"
            classification["tags"].extend(["PCI", "PAYMENT"])

        return classification

    def apply_table_tags(self, table_name: str, classification: Dict):
        """Apply classification tags to table."""
        tag_changes = []
        for tag_key, tag_value in classification.items():
            if tag_value:
                tag_changes.append(f"'{tag_key}' = '{tag_value}'")

        if tag_changes:
            sql = f"""
            ALTER TABLE {table_name}
            SET TAGS ({', '.join(tag_changes)})
            """
            self.w.statement_execution.execute_statement(
                statement=sql,
                warehouse_id=self.warehouse_id
            )
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--init` | Initialize classification framework | False |
| `--catalog` | Catalog to classify | All catalogs |
| `--schema` | Schema to classify | All schemas |
| `--auto-classify` | Use automated classification | False |
| `--rules-file` | Custom classification rules | Built-in rules |
| `--tag-pii` | Automatically tag PII | True |
| `--sensitivity` | Filter by sensitivity level | All |
| `--dry-run` | Preview without applying | False |
| `--output` | Report output path | ./classification-reports/ |

## Output Files

```
classification-reports/
├── classification-summary-{timestamp}.md
├── data-catalog-{timestamp}.json
├── unclassified-objects-{timestamp}.csv
└── classification-rules-applied-{timestamp}.log
```

## Best Practices

1. **Start with Framework**: Initialize tags and taxonomy first
2. **Iterative Classification**: Start with high-sensitivity data
3. **Validate Rules**: Test on sample data before broad application
4. **Review Automated Tags**: Human validation for critical data
5. **Document Decisions**: Maintain classification rationale
6. **Regular Updates**: Re-classify when schema changes

## Related Commands
- `/databricks-governance:scan-pii-data` - PII detection
- `/databricks-governance:setup-data-masking` - Apply masking based on classification
- `/databricks-governance:generate-compliance-report` - Compliance validation

## Agent Collaboration

This command uses these specialized agents:
- `data-classification-expert` - Classification framework design
- `data-privacy-guardian` - PII identification
- `compliance-auditor` - Regulatory mapping
- `policy-enforcer` - Policy association

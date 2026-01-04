# LLM Requirements for DevOps Integration Agents

**Document Version:** 1.0
**Last Updated:** 2026-01-03 11:11:20
**Prepared by:** Databricks Platform Team

---

## Overview

This document outlines the Large Language Model (LLM) requirements for running DevOps integration agents, including the defect management agent. The agents leverage AI/LLM capabilities for intelligent analysis, classification, and recommendations.

## Prerequisites - Environment Variables Setup

After obtaining API keys from your chosen LLM provider(s), you'll need to configure environment variables:

### Quick Setup (All Providers)

**Windows (PowerShell):**
```powershell
# Claude (Anthropic) - Recommended
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-api03-your-key-here', 'User')

# OpenAI
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')

# Azure OpenAI
[System.Environment]::SetEnvironmentVariable('AZURE_OPENAI_API_KEY', 'your-azure-key-here', 'User')
[System.Environment]::SetEnvironmentVariable('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/', 'User')

# Databricks Foundation Models
[System.Environment]::SetEnvironmentVariable('DATABRICKS_HOST', 'https://your-workspace.cloud.databricks.com', 'User')
[System.Environment]::SetEnvironmentVariable('DATABRICKS_TOKEN', 'dapi-your-token-here', 'User')

# LLM Provider Selection
[System.Environment]::SetEnvironmentVariable('LLM_PROVIDER', 'anthropic', 'User')
[System.Environment]::SetEnvironmentVariable('LLM_MODEL', 'claude-sonnet-4-5', 'User')
```

**Linux/Mac (Bash/Zsh):**
```bash
# Claude (Anthropic) - Recommended
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# OpenAI
export OPENAI_API_KEY="sk-your-key-here"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-azure-key-here"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Databricks Foundation Models
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi-your-token-here"

# LLM Provider Selection
export LLM_PROVIDER="anthropic"
export LLM_MODEL="claude-sonnet-4-5"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"' >> ~/.bashrc
echo 'export LLM_PROVIDER="anthropic"' >> ~/.bashrc
echo 'export LLM_MODEL="claude-sonnet-4-5"' >> ~/.bashrc
```

**Docker/Container Environment (.env file):**
```bash
# Claude (Anthropic) - Recommended
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Databricks Foundation Models
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi-your-token-here

# LLM Provider Selection
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-5
```

**Environment Variable Descriptions:**
- `ANTHROPIC_API_KEY`: Your Claude API key from console.anthropic.com
- `OPENAI_API_KEY`: Your OpenAI API key from platform.openai.com
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI resource key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `DATABRICKS_HOST`: Your Databricks workspace URL
- `DATABRICKS_TOKEN`: Your Databricks personal access token
- `LLM_PROVIDER`: Which provider to use (anthropic, openai, azure_openai, databricks)
- `LLM_MODEL`: Specific model to use

**Security Note:** Never commit API keys to version control. Use `.env` files in `.gitignore` or secure secret management systems like:
- Azure Key Vault
- AWS Secrets Manager
- HashiCorp Vault
- Databricks Secrets

---

## Supported LLM Providers

### 1. Claude (Anthropic) - Recommended ⭐

**Model**: Claude 3.5 Sonnet or Claude Opus 4

**Why Recommended**:
- Superior code analysis capabilities
- Excellent at root cause analysis
- Strong structured output generation
- Fast response times
- Great at following instructions

**Configuration**:
```python
# Environment variables
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export LLM_PROVIDER="claude"
export LLM_MODEL="claude-3-5-sonnet-20241022"

# Python configuration
llm_config = {
    "provider": "claude",
    "model": "claude-3-5-sonnet-20241022",
    "api_key": os.getenv("ANTHROPIC_API_KEY"),
    "temperature": 0.2,  # Lower for consistent analysis
    "max_tokens": 4096,
}
```

**API Key Setup**:
1. Visit https://console.anthropic.com/
2. Create an account or sign in
3. Navigate to API Keys
4. Click "Create Key"
5. Copy and store securely

**Pricing** (as of Jan 2026):
- Input: $3.00 / million tokens
- Output: $15.00 / million tokens
- **Estimated monthly cost**: $100-300 for moderate usage

### 2. OpenAI GPT-4

**Model**: GPT-4 Turbo or GPT-4

**Configuration**:
```python
# Environment variables
export OPENAI_API_KEY="sk-..."
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4-turbo-preview"

# Python configuration
llm_config = {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": 0.2,
    "max_tokens": 4096,
}
```

**Pricing**:
- Input: $10.00 / million tokens
- Output: $30.00 / million tokens

### 3. Azure OpenAI

**Model**: GPT-4 (via Azure)

**Configuration**:
```python
# Environment variables
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT="gpt-4"
export LLM_PROVIDER="azure_openai"

# Python configuration
llm_config = {
    "provider": "azure_openai",
    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    "api_version": "2024-02-01",
    "temperature": 0.2,
}
```

### 4. Databricks Foundation Models

**Model**: DBRX, Llama 3, or other Databricks models

**Configuration**:
```python
# Environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="dapi..."
export LLM_PROVIDER="databricks"
export LLM_MODEL="databricks-dbrx-instruct"

# Python configuration
llm_config = {
    "provider": "databricks",
    "model": "databricks-dbrx-instruct",
    "host": os.getenv("DATABRICKS_HOST"),
    "token": os.getenv("DATABRICKS_TOKEN"),
    "temperature": 0.2,
}
```

---

## LLM Capabilities Required

### 1. Code Analysis
- Parse and understand code snippets
- Identify potential bugs and issues
- Suggest fixes and improvements

### 2. Natural Language Understanding
- Parse error messages and stack traces
- Understand technical documentation
- Extract key information from logs

### 3. Classification
- Categorize defects by type
- Assess severity levels
- Determine priority

### 4. Root Cause Analysis
- Analyze error patterns
- Identify underlying issues
- Correlate multiple signals

### 5. Recommendation Generation
- Suggest fixes for identified issues
- Provide best practice guidance
- Generate implementation examples

---

## Installation & Setup

### Install LLM Client Libraries

```bash
# For Claude (Anthropic)
pip install anthropic==0.18.0

# For OpenAI
pip install openai==1.12.0

# For Azure OpenAI
pip install openai==1.12.0

# For Databricks
pip install databricks-sdk==0.18.0

# For LangChain (optional, provides unified interface)
pip install langchain==0.1.6
pip install langchain-anthropic==0.1.1
pip install langchain-openai==0.0.5
```

### Environment Variables

Create `.env` file:

```bash
# LLM Provider Configuration
LLM_PROVIDER=claude  # Options: claude, openai, azure_openai, databricks
LLM_MODEL=claude-3-5-sonnet-20241022

# Provider-specific keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
DATABRICKS_HOST=https://...
DATABRICKS_TOKEN=dapi...

# LLM Settings
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=4096
LLM_TIMEOUT=30
```

### Configuration File

Create `config/llm_config.yaml`:

```yaml
llm:
  # Provider selection
  provider: "${LLM_PROVIDER}"  # claude, openai, azure_openai, databricks
  model: "${LLM_MODEL}"

  # Generation parameters
  temperature: 0.2  # Lower = more deterministic
  max_tokens: 4096
  timeout: 30

  # Rate limiting
  requests_per_minute: 60
  tokens_per_minute: 100000

  # Retry configuration
  retry_attempts: 3
  retry_delay: 1

  # Cost controls
  max_cost_per_request: 0.10  # USD
  daily_budget: 10.00  # USD

# Provider-specific configurations
providers:
  claude:
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-5-sonnet-20241022"
    base_url: "https://api.anthropic.com"

  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4-turbo-preview"
    organization: ""  # Optional

  azure_openai:
    api_key: "${AZURE_OPENAI_API_KEY}"
    endpoint: "${AZURE_OPENAI_ENDPOINT}"
    deployment: "${AZURE_OPENAI_DEPLOYMENT}"
    api_version: "2024-02-01"

  databricks:
    host: "${DATABRICKS_HOST}"
    token: "${DATABRICKS_TOKEN}"
    model: "databricks-dbrx-instruct"
```

---

## Usage Examples

### Basic LLM Initialization

```python
from agents.llm_provider import LLMProvider

# Initialize LLM provider
llm = LLMProvider.from_env()

# Or with explicit configuration
llm = LLMProvider(
    provider="claude",
    model="claude-3-5-sonnet-20241022",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0.2,
)

# Generate response
response = llm.generate(
    prompt="Analyze this error: NullPointerException at line 42",
    max_tokens=1024,
)

print(response)
```

### Code Analysis Example

```python
from agents.defect_management import DefectAnalyzer

# Initialize analyzer
analyzer = DefectAnalyzer(llm_provider=llm)

# Analyze code for defects
code_snippet = """
def process_payment(amount):
    return api.charge(amount)  # No error handling!
"""

analysis = analyzer.analyze_code(code_snippet)

print(f"Severity: {analysis['severity']}")
print(f"Issues: {analysis['issues']}")
print(f"Recommendations: {analysis['recommendations']}")
```

### Root Cause Analysis Example

```python
# Analyze error for root cause
error_info = {
    "error_message": "NullPointerException",
    "stack_trace": "...",
    "recent_changes": [...],
}

root_cause = analyzer.identify_root_cause(error_info)

print(f"Root Cause: {root_cause['summary']}")
print(f"Affected Components: {root_cause['components']}")
print(f"Suggested Fixes: {root_cause['fixes']}")
```

---

## Performance & Cost Optimization

### Token Usage Optimization

```python
# 1. Use structured prompts
prompt = f"""Analyze this code for security issues.
Return JSON with: {{"issues": [], "severity": ""}}

Code:
{code_snippet}
"""

# 2. Set appropriate max_tokens
# Don't use 4096 if you only need 500 tokens
llm.generate(prompt, max_tokens=500)

# 3. Cache common prompts (if provider supports)
from functools import lru_cache

@lru_cache(maxsize=100)
def get_system_prompt(task_type):
    return f"You are a {task_type} specialist..."
```

### Batch Processing

```python
# Process multiple items in single call
batch_prompts = [
    f"Analyze error: {error}" for error in errors
]

# Combine into single prompt
combined = "\n\n".join([
    f"{i+1}. {prompt}"
    for i, prompt in enumerate(batch_prompts)
])

result = llm.generate(combined)
```

### Cost Tracking

```python
from agents.llm_cost_tracker import CostTracker

# Track costs
tracker = CostTracker()

with tracker.track("defect_analysis"):
    response = llm.generate(prompt)

# Get cost report
print(f"Tokens used: {tracker.total_tokens}")
print(f"Cost: ${tracker.total_cost:.4f}")
print(f"Average cost per request: ${tracker.average_cost:.4f}")
```

---

## Requirements by Agent

### Defect Management Agent

**Minimum LLM Capabilities**:
- Code analysis
- Error classification
- Root cause identification

**Recommended Models**:
- Claude 3.5 Sonnet (best performance)
- GPT-4 Turbo
- Databricks DBRX

**Estimated Token Usage**:
- Per defect analysis: 2,000-5,000 tokens
- Per root cause analysis: 3,000-8,000 tokens
- Monthly (moderate usage): 500K-1M tokens

**Estimated Monthly Cost**:
- Claude: $50-150
- OpenAI GPT-4: $150-400
- Azure OpenAI: $150-400
- Databricks: Included with workspace

---

## Troubleshooting

### Common Issues

#### 1. API Key Errors

```python
# Error: Invalid API key
# Solution: Verify key is set correctly
import os
print(os.getenv("ANTHROPIC_API_KEY"))  # Should not be None

# Check key format
# Claude: sk-ant-api03-...
# OpenAI: sk-...
```

#### 2. Rate Limiting

```python
# Error: Rate limit exceeded
# Solution: Implement retry with backoff
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(3)
)
def call_llm(prompt):
    return llm.generate(prompt)
```

#### 3. Token Limits

```python
# Error: Context length exceeded
# Solution: Truncate input or use smaller model
def truncate_text(text, max_tokens=3000):
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    return text[:max_chars]

truncated_code = truncate_text(large_code_file)
response = llm.generate(f"Analyze: {truncated_code}")
```

#### 4. Timeout Errors

```python
# Error: Request timeout
# Solution: Increase timeout or reduce input size
llm = LLMProvider(
    provider="claude",
    timeout=60,  # Increase from default 30
)
```

---

## Security & Compliance

### Data Privacy

```yaml
# What data is sent to LLM providers:
✅ Code snippets (for analysis)
✅ Error messages
✅ Stack traces
✅ Log excerpts

❌ Never send:
- User credentials
- API keys
- Personal identifiable information (PII)
- Customer data
- Proprietary algorithms (without permission)
```

### Data Sanitization

```python
import re

def sanitize_code(code):
    """Remove sensitive data before sending to LLM"""
    # Remove API keys
    code = re.sub(r'api[_-]key["\']?\s*[:=]\s*["\'][^"\']+["\']',
                  'api_key="REDACTED"', code, flags=re.IGNORECASE)

    # Remove passwords
    code = re.sub(r'password["\']?\s*[:=]\s*["\'][^"\']+["\']',
                  'password="REDACTED"', code, flags=re.IGNORECASE)

    # Remove emails
    code = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                  'user@example.com', code)

    return code

# Use before sending to LLM
sanitized = sanitize_code(original_code)
response = llm.generate(f"Analyze: {sanitized}")
```

---

## Additional Resources

- [Claude API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Databricks Foundation Models](https://docs.databricks.com/en/machine-learning/foundation-models/index.html)

---

**Maintained by**: Databricks Platform Team

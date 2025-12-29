# Manual GitHub Setup Guide

If you don't have GitHub CLI or prefer to set up manually, follow these steps:

## Method 1: GitHub Web Interface

### Step 1: Create Repository on GitHub.com

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `databricks-platform-marketplace`
   - **Description**: `Enterprise Databricks data platform plugins for Claude Code`
   - **Visibility**: Public (for marketplace distribution)
   - **Initialize**: DO NOT check "Add README" or ".gitignore"
3. Click "Create repository"

### Step 2: Push Local Code

Copy your GitHub username and run these commands:

```bash
cd databricks-platform-marketplace

# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit: Databricks Platform Marketplace v1.0.0"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/databricks-platform-marketplace.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Configure Repository Settings

On GitHub.com, go to repository Settings:

#### A. Add Topics
Settings → General → Topics
- Add: `databricks`, `data-engineering`, `claude`, `ai`, `mlops`, `delta-lake`, `pyspark`

#### B. Enable Issues
Settings → General → Features
- ✅ Check "Issues"
- ✅ Check "Discussions"

#### C. Setup GitHub Pages (for documentation)
Settings → Pages
- Source: Deploy from branch
- Branch: `main`
- Folder: `/docs`
- Click "Save"

#### D. Add Repository Secrets (for CI/CD)
Settings → Secrets and variables → Actions → New repository secret

Add these secrets:
1. `NPM_TOKEN` - Your NPM automation token
2. `DATABRICKS_HOST` - Your Databricks workspace URL
3. `DATABRICKS_TOKEN` - Your Databricks token
4. `SLACK_WEBHOOK` - Optional, for notifications

### Step 4: Create Issue Labels

Settings → Issues → Labels

Create these labels:
- `bug` (red): Something isn't working
- `enhancement` (blue): New feature or request
- `documentation` (cyan): Documentation improvements
- `good first issue` (purple): Good for newcomers
- `help wanted` (green): Extra attention needed

### Step 5: Add Collaborators (Optional)

Settings → Collaborators and teams
- Add team members with appropriate permissions

## Method 2: GitHub Desktop

### Step 1: Install GitHub Desktop
Download from: https://desktop.github.com/

### Step 2: Add Repository

1. Open GitHub Desktop
2. File → Add Local Repository
3. Choose the `databricks-platform-marketplace` folder
4. Click "Create Repository" if prompted

### Step 3: Publish to GitHub

1. Click "Publish repository"
2. Fill in details:
   - Name: `databricks-platform-marketplace`
   - Description: Enterprise Databricks data platform plugins
   - ✅ Keep code private (or uncheck for public)
3. Click "Publish repository"

### Step 4: Push Changes

1. Write commit message: "Initial commit: Databricks Platform Marketplace v1.0.0"
2. Click "Commit to main"
3. Click "Push origin"

## Method 3: Git Command Line (Manual)

If you prefer pure Git without GitHub CLI:

```bash
cd databricks-platform-marketplace

# 1. Initialize repository
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "Initial commit: Databricks Platform Marketplace v1.0.0

- Added Databricks Engineering Plugin with 15 commands
- Added 18 specialized agents for code review
- Added 8 reusable skills and templates
- Added comprehensive test suite
- Added CI/CD workflows
- Added documentation and examples"

# 4. Create main branch
git branch -M main

# 5. Add remote (create repo on github.com first)
git remote add origin https://github.com/YOUR_USERNAME/databricks-platform-marketplace.git

# 6. Push to GitHub
git push -u origin main
```

## Verify Setup

After pushing to GitHub, verify:

```bash
# Check remote
git remote -v

# Check branch
git branch -a

# Check status
git status
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/databricks-platform-marketplace.git (fetch)
origin  https://github.com/YOUR_USERNAME/databricks-platform-marketplace.git (push)
```

## Next Steps

### 1. Configure GitHub Secrets

For CI/CD to work, add secrets:

```bash
# Using GitHub CLI
gh secret set NPM_TOKEN
gh secret set DATABRICKS_HOST
gh secret set DATABRICKS_TOKEN

# Or manually via web interface
# Settings → Secrets and variables → Actions
```

### 2. Test CI/CD Pipeline

Make a small change and push:

```bash
echo "# Test" >> test.txt
git add test.txt
git commit -m "test: verify CI/CD"
git push

# Check Actions tab on GitHub
# https://github.com/YOUR_USERNAME/databricks-platform-marketplace/actions
```

### 3. Install Plugin

```bash
# Add marketplace
claude /plugin marketplace add https://github.com/YOUR_USERNAME/databricks-platform-marketplace

# Install plugin
claude /plugin install databricks-engineering

# Verify
claude /plugin list
```

### 4. Test Commands

```bash
# Test a command
claude /databricks:plan-pipeline "test pipeline"

# If it works, you're all set! 🎉
```

## Troubleshooting

### Authentication Issues

If you get authentication errors:

```bash
# Using HTTPS with token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/databricks-platform-marketplace.git

# Or use SSH
git remote set-url origin git@github.com:YOUR_USERNAME/databricks-platform-marketplace.git
```

### Push Rejected

If push is rejected:

```bash
# Pull first (if repo has README)
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

### Large Files

If you get errors about large files:

```bash
# Check file sizes
du -sh * | sort -h

# Remove large files from history if needed
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/large/file' \
  --prune-empty --tag-name-filter cat -- --all
```

## Getting Help

- GitHub Docs: https://docs.github.com
- Git Docs: https://git-scm.com/doc
- GitHub Community: https://github.community

---

**Once setup is complete, your repository will be live at:**
`https://github.com/YOUR_USERNAME/databricks-platform-marketplace`

You can then share it with others to install:
```bash
claude /plugin marketplace add https://github.com/YOUR_USERNAME/databricks-platform-marketplace
```

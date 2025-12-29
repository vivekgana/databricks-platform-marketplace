# Deployment Guide

This guide explains how to deploy the Databricks Platform Marketplace to GitHub and publish it as a third-party marketplace.

## Prerequisites

- GitHub account
- NPM account (for publishing)
- Git installed locally
- Repository cloned locally

## Step 1: Prepare Repository

### 1.1 Initialize Git Repository

```bash
cd databricks-platform-marketplace
git init
git add .
git commit -m "Initial commit: Databricks Platform Marketplace v1.0.0"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `databricks-platform-marketplace`
3. Do NOT initialize with README (we already have one)
4. Make it public for marketplace distribution

### 1.3 Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOURUSERNAME/databricks-platform-marketplace.git

# Push to main
git branch -M main
git push -u origin main
```

## Step 2: Configure GitHub Secrets

Add these secrets in GitHub Settings → Secrets and variables → Actions:

### Required Secrets

```
NPM_TOKEN                    # NPM publish token
DATABRICKS_HOST              # For integration tests
DATABRICKS_TOKEN             # For integration tests
DATABRICKS_WAREHOUSE_ID      # For integration tests (optional)
SLACK_WEBHOOK                # For notifications (optional)
```

### How to Get Secrets

**NPM Token:**
1. Login to npmjs.com
2. Go to Access Tokens
3. Generate new token (Automation type)
4. Copy token to GitHub secret

**Databricks Credentials:**
1. Use test workspace credentials
2. Create service principal for CI/CD
3. Grant necessary permissions

## Step 3: Publish to NPM

### 3.1 Manual Publish

```bash
# Login to NPM
npm login

# Publish package
npm publish --access public
```

### 3.2 Automated Publish

Pushing a tag triggers automatic publishing:

```bash
# Create and push tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will:
# 1. Run all tests
# 2. Validate plugins
# 3. Publish to NPM
# 4. Create GitHub release
```

## Step 4: Test Installation

### Test NPM Installation

```bash
# Install from NPM
npx claude-plugins install @yourcompany/databricks-platform-marketplace/databricks-engineering

# Verify installation
claude /plugin list
```

### Test GitHub Installation

```bash
# Install from GitHub
claude /plugin marketplace add https://github.com/yourcompany/databricks-platform-marketplace
claude /plugin install databricks-engineering

# Verify installation
claude /plugin list
```

## Step 5: Setup Documentation Site

### Using GitHub Pages

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Build docs
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

Documentation will be available at:
`https://yourcompany.github.io/databricks-platform-marketplace`

### Custom Domain (Optional)

1. Add CNAME file:
   ```bash
   echo "docs.yourcompany.com" > docs/CNAME
   ```

2. Configure DNS:
   ```
   Type: CNAME
   Name: docs
   Value: yourcompany.github.io
   ```

3. Enable in GitHub Settings → Pages

## Step 6: Setup Monitoring

### NPM Download Statistics

Monitor at: https://npm-stat.com/charts.html?package=@yourcompany/databricks-platform-marketplace

### GitHub Insights

Track at: https://github.com/yourcompany/databricks-platform-marketplace/pulse

### Setup Alerts

Add to `.github/workflows/alerts.yml`:

```yaml
name: Weekly Stats

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  stats:
    runs-on: ubuntu-latest
    steps:
      - name: Get download stats
        run: |
          curl -s https://api.npmjs.org/downloads/point/last-week/@yourcompany/databricks-platform-marketplace
      
      - name: Post to Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "📊 Weekly Marketplace Stats"
            }
```

## Step 7: Community Setup

### Create Discussion Board

1. Go to Settings → Features
2. Enable Discussions
3. Create categories:
   - General
   - Q&A
   - Feature Requests
   - Show and Tell

### Setup Issue Templates

Already included in `.github/ISSUE_TEMPLATE/`

### Create Slack Community

1. Create workspace: yourcompany.slack.com
2. Create channels:
   - `#general`
   - `#help`
   - `#announcements`
   - `#contributors`
3. Add Slack link to README

## Step 8: Marketing

### Add Badges to README

```markdown
[![NPM Version](https://img.shields.io/npm/v/@yourcompany/databricks-platform-marketplace.svg)](https://www.npmjs.com/package/@yourcompany/databricks-platform-marketplace)
[![Downloads](https://img.shields.io/npm/dt/@yourcompany/databricks-platform-marketplace.svg)](https://www.npmjs.com/package/@yourcompany/databricks-platform-marketplace)
[![GitHub Stars](https://img.shields.io/github/stars/yourcompany/databricks-platform-marketplace.svg)](https://github.com/yourcompany/databricks-platform-marketplace/stargazers)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
```

### Create Demo Video

1. Record 5-minute demo
2. Upload to YouTube
3. Add to README
4. Share on social media

### Write Blog Post

Topics to cover:
- Why we built this
- Key features
- Getting started guide
- Example use cases
- Future roadmap

### Share on Platforms

- Dev.to
- Medium
- LinkedIn
- Twitter
- Reddit (r/databricks, r/dataengineering)
- Hacker News

## Step 9: Maintenance Plan

### Weekly Tasks

- [ ] Review and respond to issues
- [ ] Merge approved PRs
- [ ] Update dependencies
- [ ] Check CI/CD health

### Monthly Tasks

- [ ] Review analytics
- [ ] Update documentation
- [ ] Plan new features
- [ ] Community engagement

### Quarterly Tasks

- [ ] Major version planning
- [ ] User surveys
- [ ] Performance optimization
- [ ] Security audits

## Troubleshooting Deployment

### NPM Publish Fails

```bash
# Check authentication
npm whoami

# Verify package name is available
npm view @yourcompany/databricks-platform-marketplace

# Check for errors in package.json
npm pack --dry-run
```

### GitHub Actions Fails

```bash
# Check workflow logs
gh run list
gh run view <run-id>

# Test locally
act push
```

### Documentation Build Fails

```bash
# Test locally
mkdocs serve

# Check for broken links
mkdocs build --strict
```

## Rollback Procedure

If a release has issues:

### 1. Deprecate NPM Version

```bash
npm deprecate @yourcompany/databricks-platform-marketplace@1.0.1 "Use version 1.0.0 instead"
```

### 2. Revert GitHub Release

```bash
git revert HEAD
git push origin main
```

### 3. Notify Users

- Post in Slack
- GitHub discussion
- Update README

## Support Plan

### Response Times

- Critical bugs: < 24 hours
- Feature requests: < 7 days
- Questions: < 48 hours

### Support Channels

1. GitHub Issues (primary)
2. Slack community
3. Email support
4. Documentation

## Success Metrics

Track these KPIs:

- NPM downloads per week
- GitHub stars and forks
- Active users
- Issue resolution time
- Community engagement
- User satisfaction scores

## Next Steps

After successful deployment:

1. Monitor first week metrics
2. Address any immediate issues
3. Engage with early adopters
4. Plan v1.1.0 features
5. Build community

---

## Checklist

Use this checklist for deployment:

- [ ] Repository created on GitHub
- [ ] GitHub secrets configured
- [ ] NPM account ready
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Published to NPM
- [ ] GitHub release created
- [ ] Documentation site live
- [ ] Community channels setup
- [ ] Monitoring in place
- [ ] Blog post published
- [ ] Social media shared

---

**Good luck with your marketplace launch!** 🚀

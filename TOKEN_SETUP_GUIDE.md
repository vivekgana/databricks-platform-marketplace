# GitHub Token Authentication Guide

Since GitHub CLI cannot be installed in this environment, we'll use **Git + GitHub Token** directly. This is even simpler!

## 📝 What You Need

1. **GitHub Personal Access Token** - You mentioned you have this
2. **Git** - Already installed ✅
3. **Your GitHub username**

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get Your GitHub Token Ready

If you don't have a token yet, create one:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: `databricks-marketplace`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `write:packages` (Upload packages)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again)

### Step 2: Run the Setup Script

```bash
cd databricks-platform-marketplace
./github-push-with-token.sh
```

The script will ask you for:
1. **GitHub username**: Your username (e.g., `johndoe`)
2. **GitHub token**: Paste your token (input is hidden for security)
3. **Repository name**: Press Enter for default (`databricks-platform-marketplace`)
4. **Visibility**: `public` or `private` (default: public)

### Step 3: Confirm and Wait

The script will:
- ✅ Initialize git repository
- ✅ Create repository on GitHub
- ✅ Push all code
- ✅ Setup GitHub Pages for docs
- ✅ Add repository topics
- ✅ Create issue labels
- ✅ Configure everything

Takes about 1-2 minutes!

## 🎯 What the Script Does

### 1. Creates Repository via GitHub API
```bash
POST https://api.github.com/user/repos
```

### 2. Pushes Code with Token Auth
```bash
git push https://TOKEN@github.com/USER/REPO.git
```

### 3. Configures Repository
- Adds topics: databricks, data-engineering, claude, ai, mlops
- Creates issue labels: bug, enhancement, documentation
- Enables GitHub Pages on `/docs` folder
- Sets up repository description

### 4. Secures Credentials
- Removes token from git config after push
- Uses secure HTTPS authentication

## ✅ After Setup

Once complete, you'll see:

```
╔════════════════════════════════════════════════════════╗
║   ✅ GitHub Setup Complete!                            ║
╚════════════════════════════════════════════════════════╝

📍 Repository Details:
   URL:      https://github.com/yourusername/databricks-platform-marketplace
   Clone:    git clone https://github.com/yourusername/databricks-platform-marketplace.git
```

### Install the Plugin

```bash
# Add marketplace
claude /plugin marketplace add https://github.com/YOURUSERNAME/databricks-platform-marketplace

# Install plugin
claude /plugin install databricks-engineering

# Test it
claude /databricks:plan-pipeline "test pipeline"
```

## 🔐 Configure GitHub Secrets (Optional)

For CI/CD automation, add these secrets:

1. Go to: `https://github.com/YOURUSERNAME/databricks-platform-marketplace/settings/secrets/actions`
2. Click "New repository secret"
3. Add:
   - `NPM_TOKEN` - For publishing to NPM
   - `DATABRICKS_HOST` - For integration tests
   - `DATABRICKS_TOKEN` - For integration tests
   - `SLACK_WEBHOOK` - For notifications (optional)

## 🐛 Troubleshooting

### "Authentication failed"
- Check your token has correct permissions: `repo`, `workflow`
- Make sure token hasn't expired
- Try generating a new token

### "Repository already exists"
- The script will use the existing repo
- Your code will still be pushed
- You may need to force push

### "Permission denied"
- Ensure token has `repo` scope
- Check if 2FA is required on your account

### "Network error"
If network is restricted, use manual method:

1. Create repo on github.com manually
2. Use this command to push:
```bash
git remote add origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
git push -u origin main
```

## 📱 Alternative: GitHub Web Interface

If you prefer manual control:

1. Create repo at https://github.com/new
2. Push with token:
```bash
git remote add origin https://YOUR_TOKEN@github.com/USERNAME/databricks-platform-marketplace.git
git push -u origin main
```

## 🔒 Security Best Practices

1. **Never commit your token** to the repository
2. **Set token expiration** (30-90 days recommended)
3. **Use fine-grained tokens** when possible
4. **Rotate tokens regularly**
5. **Revoke old tokens** you're not using

## 📞 Need Help?

If you encounter issues:

1. Check the script output for error messages
2. Verify your token at: https://github.com/settings/tokens
3. Try the manual push method above
4. Check GitHub's status: https://www.githubstatus.com/

## ✨ Ready to Go!

Run this command and you'll be set up in minutes:

```bash
./github-push-with-token.sh
```

Make sure you have your GitHub token ready to paste when prompted! 🎉

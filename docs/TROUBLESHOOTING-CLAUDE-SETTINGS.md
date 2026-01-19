# Troubleshooting Claude Settings.json on Windows

**Document Version:** 1.0
**Last Updated:** 2026-01-05 10:31:10
**Prepared by:** Databricks Platform Team

---

## Overview

This guide helps troubleshoot issues when Claude Code CLI does not read the `settings.json` file from the user profile directory on Windows machines.

## Common Issue

**Symptom:** Claude Code does not recognize environment variables or settings configured in `%USERPROFILE%\.claude\settings.json`

**Expected Behavior:** Claude should automatically read settings from:
- `C:\Users\{username}\.claude\settings.json`

---

## Troubleshooting Steps

### Step 1: Verify HOME Environment Variable

Claude Code uses the `HOME` environment variable to locate configuration files. On Windows, this should be set to `USERPROFILE`.

**Check if HOME is set:**

```powershell
# PowerShell
$env:HOME
$env:USERPROFILE

# Should both point to: C:\Users\{username}
```

```cmd
# Command Prompt
echo %HOME%
echo %USERPROFILE%

# Should both show: C:\Users\{username}
```

**If HOME is not set or different from USERPROFILE:**

```powershell
# PowerShell - Set for current session
$env:HOME = $env:USERPROFILE

# PowerShell - Set permanently for user
[System.Environment]::SetEnvironmentVariable('HOME', $env:USERPROFILE, 'User')

# Verify
$env:HOME
```

```cmd
# Command Prompt - Set permanently for user
setx HOME %USERPROFILE%

# Close and reopen terminal, then verify
echo %HOME%
```

**Restart your terminal or IDE** after setting the environment variable permanently.

---

### Step 2: Verify Settings File Location

**Check if settings.json exists:**

```powershell
# PowerShell
Test-Path "$env:USERPROFILE\.claude\settings.json"
# Should return: True

# Show file contents
Get-Content "$env:USERPROFILE\.claude\settings.json"
```

```cmd
# Command Prompt
dir %USERPROFILE%\.claude\settings.json

# Show file contents
type %USERPROFILE%\.claude\settings.json
```

**If file does not exist:**

```powershell
# PowerShell - Create directory
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"

# Create settings.json
@"
{
  "env": {
    "ANTHROPIC_MODEL": "databricks-claude-sonnet-4-5",
    "ANTHROPIC_BASE_URL": "https://your-workspace.azuredatabricks.net/serving-endpoints/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your-databricks-token"
  }
}
"@ | Out-File -FilePath "$env:USERPROFILE\.claude\settings.json" -Encoding UTF8
```

---

### Step 3: Verify JSON Syntax

**Invalid JSON is a common cause of settings not loading.**

**Validate JSON syntax:**

```powershell
# PowerShell - Test JSON validity
try {
    Get-Content "$env:USERPROFILE\.claude\settings.json" -Raw | ConvertFrom-Json
    Write-Host "JSON is valid" -ForegroundColor Green
} catch {
    Write-Host "JSON is INVALID: $_" -ForegroundColor Red
}
```

**Common JSON errors:**
- ❌ Trailing commas: `"key": "value",}`
- ❌ Missing quotes: `{key: "value"}`
- ❌ Single quotes instead of double: `{'key': 'value'}`
- ❌ Comments (not allowed in JSON): `// comment`

**Valid settings.json example:**

```json
{
  "env": {
    "ANTHROPIC_MODEL": "databricks-claude-sonnet-4-5",
    "ANTHROPIC_BASE_URL": "https://your-workspace.azuredatabricks.net/serving-endpoints/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "dapi_your_databricks_token_here",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "databricks-claude-opus-4-1",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "databricks-claude-sonnet-4-5"
  },
  "enabledPlugins": {
    "sdlc@danielscholl": true
  }
}
```

---

### Step 4: Check File Permissions

**Verify that Claude can read the file:**

```powershell
# PowerShell - Check file permissions
Get-Acl "$env:USERPROFILE\.claude\settings.json" | Format-List

# Check if current user has read access
$acl = Get-Acl "$env:USERPROFILE\.claude\settings.json"
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$acl.Access | Where-Object { $_.IdentityReference -eq $currentUser }
```

**If permissions are incorrect:**

```powershell
# PowerShell - Grant read permissions to current user
$path = "$env:USERPROFILE\.claude\settings.json"
$acl = Get-Acl $path
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$permission = New-Object System.Security.AccessControl.FileSystemAccessRule($currentUser, "Read", "Allow")
$acl.SetAccessRule($permission)
Set-Acl $path $acl
```

---

### Step 5: Check for File Encoding Issues

**Claude requires UTF-8 encoding without BOM (Byte Order Mark).**

```powershell
# PowerShell - Check file encoding
$bytes = [System.IO.File]::ReadAllBytes("$env:USERPROFILE\.claude\settings.json")
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "File has UTF-8 BOM (may cause issues)" -ForegroundColor Yellow
} else {
    Write-Host "File encoding looks good" -ForegroundColor Green
}

# Fix: Convert to UTF-8 without BOM
$content = Get-Content "$env:USERPROFILE\.claude\settings.json" -Raw
[System.IO.File]::WriteAllText("$env:USERPROFILE\.claude\settings.json", $content, [System.Text.UTF8Encoding]::new($false))
```

---

### Step 6: Verify Claude Installation

**Check Claude Code version and installation:**

```bash
# Check Claude Code version
claude --version

# Check where Claude is installed
where claude

# Check Claude config location (should show .claude directory)
claude config --list
```

**If Claude is not found:**
- Reinstall Claude Code CLI
- Add Claude to PATH environment variable
- Restart terminal after installation

---

### Step 7: Check for Conflicting Configuration

**Claude may read settings from multiple locations. Check all possible locations:**

```powershell
# PowerShell - Check all possible config locations
$locations = @(
    "$env:USERPROFILE\.claude\settings.json",
    "$env:HOME\.claude\settings.json",
    "$env:APPDATA\.claude\settings.json",
    "$env:LOCALAPPDATA\.claude\settings.json",
    "$(Get-Location)\.claude\settings.json"
)

foreach ($loc in $locations) {
    if (Test-Path $loc) {
        Write-Host "Found: $loc" -ForegroundColor Green
        Write-Host "Content:"
        Get-Content $loc
        Write-Host "`n---`n"
    } else {
        Write-Host "Not found: $loc" -ForegroundColor Gray
    }
}
```

**If multiple settings files exist:**
- Claude typically prioritizes: Project-local > User profile > System
- Remove or consolidate conflicting files
- Keep only `%USERPROFILE%\.claude\settings.json` for user-wide settings

---

### Step 8: Enable Claude Debug Logging

**Enable verbose logging to see what Claude is reading:**

```bash
# Run Claude with debug logging
claude --verbose --log-level debug your-command

# Or set environment variable
export CLAUDE_LOG_LEVEL=debug
claude your-command
```

```powershell
# PowerShell
$env:CLAUDE_LOG_LEVEL = "debug"
claude your-command
```

**Look for lines indicating where Claude is reading settings from:**
- "Loading settings from: ..."
- "Config file not found: ..."
- "Failed to parse settings: ..."

---

### Step 9: Test with Minimal Settings

**Create a minimal settings.json to isolate the issue:**

```json
{
  "env": {
    "TEST_VAR": "test_value"
  }
}
```

**Test if Claude reads this variable:**

```bash
# In Claude session, check if TEST_VAR is available
echo $TEST_VAR
# Or in PowerShell
echo $env:TEST_VAR
```

**If minimal settings work:**
- Gradually add settings back to identify which setting causes the issue
- Check for special characters or invalid values

---

### Step 10: Check Windows User Profile Path

**Some Windows configurations have unusual user profile paths:**

```powershell
# PowerShell - Check all user-related paths
Write-Host "USERPROFILE: $env:USERPROFILE"
Write-Host "HOME: $env:HOME"
Write-Host "HOMEDRIVE: $env:HOMEDRIVE"
Write-Host "HOMEPATH: $env:HOMEPATH"
Write-Host "APPDATA: $env:APPDATA"
Write-Host "LOCALAPPDATA: $env:LOCALAPPDATA"

# Check if user profile contains special characters or spaces
if ($env:USERPROFILE -match '[\[\]\(\)\s]') {
    Write-Host "WARNING: User profile path contains special characters or spaces" -ForegroundColor Yellow
    Write-Host "This may cause issues with some tools"
}
```

**If user profile path has issues:**
- Try setting an explicit CLAUDE_CONFIG_DIR environment variable:
  ```powershell
  [System.Environment]::SetEnvironmentVariable('CLAUDE_CONFIG_DIR', 'C:\claude-config', 'User')
  ```
- Move settings.json to this explicit location

---

## Complete Diagnostic Script

**Run this comprehensive diagnostic script:**

```powershell
# Save as: test-claude-settings.ps1

Write-Host "=== Claude Settings Diagnostic ===" -ForegroundColor Cyan
Write-Host ""

# 1. Environment Variables
Write-Host "[1] Environment Variables:" -ForegroundColor Yellow
Write-Host "USERPROFILE: $env:USERPROFILE"
Write-Host "HOME: $env:HOME"
if ($env:HOME -ne $env:USERPROFILE) {
    Write-Host "WARNING: HOME != USERPROFILE" -ForegroundColor Red
    Write-Host "RECOMMENDATION: Set HOME=$env:USERPROFILE" -ForegroundColor Yellow
}
Write-Host ""

# 2. Settings File Existence
Write-Host "[2] Settings File Location:" -ForegroundColor Yellow
$settingsPath = "$env:USERPROFILE\.claude\settings.json"
if (Test-Path $settingsPath) {
    Write-Host "✓ Found: $settingsPath" -ForegroundColor Green
} else {
    Write-Host "✗ NOT FOUND: $settingsPath" -ForegroundColor Red
    Write-Host "RECOMMENDATION: Create the file" -ForegroundColor Yellow
}
Write-Host ""

# 3. JSON Validity
Write-Host "[3] JSON Validity:" -ForegroundColor Yellow
if (Test-Path $settingsPath) {
    try {
        $json = Get-Content $settingsPath -Raw | ConvertFrom-Json
        Write-Host "✓ JSON is valid" -ForegroundColor Green
        Write-Host "Settings preview:"
        $json | ConvertTo-Json -Depth 2
    } catch {
        Write-Host "✗ JSON is INVALID" -ForegroundColor Red
        Write-Host "ERROR: $_" -ForegroundColor Red
        Write-Host "RECOMMENDATION: Fix JSON syntax" -ForegroundColor Yellow
    }
} else {
    Write-Host "- Skipped (file not found)" -ForegroundColor Gray
}
Write-Host ""

# 4. File Permissions
Write-Host "[4] File Permissions:" -ForegroundColor Yellow
if (Test-Path $settingsPath) {
    $acl = Get-Acl $settingsPath
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $userAccess = $acl.Access | Where-Object { $_.IdentityReference -match $currentUser.Split('\')[-1] }
    if ($userAccess) {
        Write-Host "✓ Current user has access: $($userAccess.FileSystemRights)" -ForegroundColor Green
    } else {
        Write-Host "✗ Current user may not have access" -ForegroundColor Red
        Write-Host "RECOMMENDATION: Check file permissions" -ForegroundColor Yellow
    }
} else {
    Write-Host "- Skipped (file not found)" -ForegroundColor Gray
}
Write-Host ""

# 5. File Encoding
Write-Host "[5] File Encoding:" -ForegroundColor Yellow
if (Test-Path $settingsPath) {
    $bytes = [System.IO.File]::ReadAllBytes($settingsPath)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "⚠ File has UTF-8 BOM" -ForegroundColor Yellow
        Write-Host "RECOMMENDATION: Convert to UTF-8 without BOM" -ForegroundColor Yellow
    } else {
        Write-Host "✓ File encoding looks good" -ForegroundColor Green
    }
} else {
    Write-Host "- Skipped (file not found)" -ForegroundColor Gray
}
Write-Host ""

# 6. Claude Installation
Write-Host "[6] Claude Installation:" -ForegroundColor Yellow
$claudePath = (Get-Command claude -ErrorAction SilentlyContinue)
if ($claudePath) {
    Write-Host "✓ Claude found at: $($claudePath.Source)" -ForegroundColor Green
    Write-Host "Version: $(claude --version 2>&1)" -ForegroundColor Green
} else {
    Write-Host "✗ Claude not found in PATH" -ForegroundColor Red
    Write-Host "RECOMMENDATION: Install Claude Code CLI or add to PATH" -ForegroundColor Yellow
}
Write-Host ""

# 7. Summary
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "If all checks pass but Claude still doesn't read settings:"
Write-Host "1. Restart your terminal/IDE"
Write-Host "2. Run Claude with debug logging: claude --verbose --log-level debug"
Write-Host "3. Check for conflicting project-local .claude/settings.json files"
Write-Host "4. Contact support with the output of this diagnostic script"
Write-Host ""
```

**Run the diagnostic:**

```powershell
# Run directly
powershell -ExecutionPolicy Bypass -File test-claude-settings.ps1

# Or save and run
.\test-claude-settings.ps1
```

---

## Quick Fix Checklist

For other users experiencing issues, have them run this quick checklist:

### ✅ Quick Fix Commands

```powershell
# 1. Set HOME environment variable
[System.Environment]::SetEnvironmentVariable('HOME', $env:USERPROFILE, 'User')

# 2. Create .claude directory if missing
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude"

# 3. Create settings.json (replace with actual values)
@"
{
  "env": {
    "ANTHROPIC_MODEL": "databricks-claude-sonnet-4-5",
    "ANTHROPIC_BASE_URL": "https://your-workspace.azuredatabricks.net/serving-endpoints/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your-databricks-token"
  }
}
"@ | Out-File -FilePath "$env:USERPROFILE\.claude\settings.json" -Encoding UTF8

# 4. Validate JSON
Get-Content "$env:USERPROFILE\.claude\settings.json" -Raw | ConvertFrom-Json

# 5. Restart terminal/IDE
Write-Host "Settings created. Please RESTART your terminal/IDE" -ForegroundColor Green
```

---

## Common Issues and Solutions

### Issue 1: HOME not set
**Symptom:** Claude looks in wrong directory
**Solution:**
```powershell
[System.Environment]::SetEnvironmentVariable('HOME', $env:USERPROFILE, 'User')
# Restart terminal
```

### Issue 2: JSON syntax error
**Symptom:** Settings file exists but Claude ignores it
**Solution:**
- Validate JSON with online validator (jsonlint.com)
- Remove trailing commas
- Use double quotes, not single quotes
- Remove comments

### Issue 3: UTF-8 BOM encoding
**Symptom:** File exists and JSON is valid, but Claude doesn't read it
**Solution:**
```powershell
$content = Get-Content "$env:USERPROFILE\.claude\settings.json" -Raw
[System.IO.File]::WriteAllText("$env:USERPROFILE\.claude\settings.json", $content, [System.Text.UTF8Encoding]::new($false))
```

### Issue 4: Wrong file location
**Symptom:** Settings in wrong directory
**Solution:**
- Settings must be in `%USERPROFILE%\.claude\settings.json`
- Not in project directory (unless project-specific override)
- Not in `%APPDATA%` or `%LOCALAPPDATA%`

### Issue 5: Need to restart IDE/terminal
**Symptom:** Changed settings but Claude doesn't see them
**Solution:**
- Close and reopen terminal
- Restart IDE (VS Code, etc.)
- Environment variables require new process

---

## Enterprise/Domain-Joined Windows Issues

### Roaming Profiles
If users have roaming profiles:
```powershell
# Check if profile is roaming
$profileType = (Get-WmiObject Win32_UserProfile | Where-Object { $_.LocalPath -eq $env:USERPROFILE }).ProfileType
if ($profileType -eq 1) {
    Write-Host "Roaming profile detected"
    # Settings may sync across machines
}
```

### Redirected Folders
If Documents/AppData are redirected:
```powershell
# Check for folder redirection
Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
```

### Network Drive Home Directories
If `%HOME%` points to network drive:
```powershell
# Create local .claude directory instead
$localConfig = "$env:LOCALAPPDATA\.claude"
New-Item -ItemType Directory -Force -Path $localConfig
# Copy settings.json there and set CLAUDE_CONFIG_DIR
```

---

## Support Information

If none of these solutions work:

1. **Collect diagnostic information:**
   ```powershell
   # Run diagnostic script and save output
   .\test-claude-settings.ps1 > claude-diagnostic.txt
   ```

2. **Include in support request:**
   - Diagnostic script output
   - Claude version (`claude --version`)
   - Windows version (`winver`)
   - Settings file content (redact sensitive tokens)
   - Error messages from debug logging

3. **Contact:**
   - Email: data-platform@vivekgana.com
   - Include "Claude Settings Issue" in subject

---

## Related Documentation

- [Configuration Reference](configuration.md)
- [Getting Started Guide](getting-started.md)
- [API Reference](api-reference.md)

---

**Prepared by:** Databricks Platform Team
**Contact:** data-platform@vivekgana.com

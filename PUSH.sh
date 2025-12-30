#!/bin/bash
# One-line push script - Run this on your local machine

echo "🚀 Pushing to GitHub..."
git push -u origin main && echo "✅ SUCCESS! Repository live at: https://github.com/vivekgana/databricks-platform-marketplace" || echo "❌ Push failed. See FINAL_PUSH_INSTRUCTIONS.md for troubleshooting"

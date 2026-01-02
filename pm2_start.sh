#!/usr/bin/env bash
set -euo pipefail

# Ensure logs dir exists and start via PM2 using ecosystem.config.js
mkdir -p logs

if ! command -v pm2 >/dev/null 2>&1; then
  echo "pm2 not found. Install with: npm install -g pm2"
  exit 1
fi

pm2 start ecosystem.config.js
pm2 save
echo "PM2 started apps. Use 'pm2 logs monthly-workflow' to follow logs."

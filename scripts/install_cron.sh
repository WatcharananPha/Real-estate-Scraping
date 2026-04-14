#!/usr/bin/env bash
set -euo pipefail
CRON_CMD="/home/kongla/Documents/GitHub/Real-estate-Scraping/scripts/run_jupyter_notebooks.sh >> /home/kongla/Documents/GitHub/Real-estate-Scraping/logs/run_notebooks.log 2>&1"
CRON_LINE="0 0 * * * $CRON_CMD"

# Check if the cron line already exists
existing="$(crontab -l 2>/dev/null || true)"
if echo "$existing" | grep -F -- "$CRON_CMD" >/dev/null 2>&1; then
  echo "Crontab entry already present."
  exit 0
fi

# Install new crontab entry
{
  echo "$existing"
  echo "$CRON_LINE"
} | crontab -

echo "Installed crontab:"
crontab -l

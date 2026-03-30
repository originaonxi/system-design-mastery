#!/usr/bin/env bash
# Auto-commits newly generated lessons to git every run
# Run via: while true; do bash scripts/auto_commit.sh; sleep 1800; done
set -euo pipefail

cd "$(dirname "$0")/.."

# Count new untracked + modified lesson files
NEW_FILES=$(git status --porcelain lessons/ | wc -l | tr -d ' ')

if [ "$NEW_FILES" -eq 0 ]; then
    echo "[$(date)] No new lessons to commit"
    exit 0
fi

# Get count of generated lessons
GENERATED=$(ls lessons/*.html 2>/dev/null | wc -l | tr -d ' ')

echo "[$(date)] Committing $NEW_FILES new files ($GENERATED total lessons generated)"

git add lessons/*.html lessons/*.json generation_progress.json 2>/dev/null || true
git commit -m "Add pre-generated lessons (${GENERATED}/200 complete)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
git push
echo "[$(date)] Pushed successfully"

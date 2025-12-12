---
allowed-tools: Bash(git push:*), Bash(git status:*), Bash(git log:*)
description: Push committed changes to remote repository
---

# Publish Agent State

Push all committed local changes to the remote GitHub repository.

## Context

- Current branch: !`git branch --show-current`
- Unpushed commits: !`git log --oneline origin/main..HEAD 2>/dev/null || echo "No unpushed commits or no remote tracking"`
- Working tree status: !`git status --short`

## Pre-Push Checks

1. **Check for uncommitted changes**
   - If there are uncommitted changes, warn the user
   - Suggest running `/commit` first

2. **Check for unpushed commits**
   - If no commits to push, inform the user and exit
   - Show what commits will be pushed

## Execution

```bash
git push origin main
```

## Error Handling

**If push is rejected:**
- Remote has new commits that need to be pulled first
- Suggest running `/sync` instead (which handles pull + push)

**If authentication fails:**
- Check that SSH key or credentials are configured
- For Trinity deployment, ensure deploy key is set up

## Post-Push Report

After successful push:
- Confirm commits were pushed
- Show the remote repository URL
- Confirm sync status

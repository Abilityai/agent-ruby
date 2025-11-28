---
allowed-tools: Bash(git pull:*), Bash(git push:*), Bash(git status:*), Bash(git stash:*), Bash(git log:*), Bash(git fetch:*)
description: Sync agent state with remote repository (pull then push)
---

# Sync Agent State

Synchronize the local agent state with the remote GitHub repository.

## Context

- Current branch: !`git branch --show-current`
- Remote tracking: !`git status -sb`
- Pending commits: !`git log --oneline origin/main..HEAD 2>/dev/null || echo "No remote tracking yet"`

## Instructions

### Step 1: Fetch and Check Status

```bash
git fetch origin
git status
```

### Step 2: Pull Changes (with rebase to keep history clean)

```bash
git pull --rebase origin main
```

**If conflicts occur:**
1. List the conflicting files
2. Show the conflict markers
3. Ask the user how to resolve (keep ours, keep theirs, or manual)
4. After resolution: `git add <resolved-files>` then `git rebase --continue`

### Step 3: Push Local Commits

```bash
git push origin main
```

**If push fails** (rejected due to remote changes):
1. Pull again with rebase
2. Resolve any new conflicts
3. Push again

## Safety Checks

- Never force push (`git push --force`) without explicit user approval
- Always show what will be pushed before pushing
- Warn if there are uncommitted changes (suggest `/commit` first)

## Post-Sync Report

After successful sync, report:
- Number of commits pulled
- Number of commits pushed
- Current sync status with remote

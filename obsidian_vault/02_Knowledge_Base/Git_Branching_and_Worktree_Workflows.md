---
title: Git Worktrees, Interactive Rebase & Disaster Recovery
category: Full-Stack & Systems Engineering
tags: [git, devops, vcs, workflow, productivity]
created: 2026-11-01
status: ACTIVE
related: "[[Linux_CLI_and_System_Administration]], [[Docker_Containerization_Internals]], [[Deep_Work_and_Cognitive_Focus]]"
---

# Git Worktrees, Interactive Rebase & Disaster Recovery

**Git** manages distributed revision control by storing snapshots of project states as an immutable Directed Acyclic Graph (DAG) of commit objects.

## Git Worktree Superpowers
`git worktree` allows checking out multiple branches simultaneously into separate directories linked to the same underlying `.git` repository:
- `git worktree add ../hotfix-branch hotfix`: Immediately work on an urgent bug without stashing or switching branches in your main directory.
- `git worktree remove ../hotfix-branch`: Clean up temporary work environments cleanly.

## Interactive Rebase & Reflog Recovery
- **Interactive Rebase (`git rebase -i HEAD~N`):** Reorder, squash, edit, or drop commits to maintain a clean linear project history.
- **Reflog (`git reflog`):** The local flight recorder tracking every movement of `HEAD`. Even if a branch is deleted or a rebase goes wrong, lost commits can be recovered using `git reset --hard HEAD@{n}`.

See also: [[Linux_CLI_and_System_Administration]], [[Deep_Work_and_Cognitive_Focus]], [[Docker_Containerization_Internals]].

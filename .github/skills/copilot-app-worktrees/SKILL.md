---
name: "copilot-app-worktrees"
description: "Navigate Copilot App sessions, worktrees, source-owned resources, handoffs, and recovery"
domain: "workflow-coordination"
confidence: "high"
source: "repository"
---

## Session and worktree boundaries

Treat every Copilot App coding session as an isolated checkout/worktree unless the App reports
otherwise. Start by identifying the session, absolute worktree path, branch, and repository.
Inspect `git status --short --branch` there before editing. Never assume another session's
uncommitted files are visible in the current checkout.

Use separate worktrees for independent concurrent changes. Avoid branch switching in a shared
checkout, especially while another session may be using it. Do not remove a worktree until its
changes are merged, explicitly abandoned, or handed off for preservation.

## Source-of-truth handling

`.github/skills/**` and tracked `.squad/**` files belong to the source repository and must be
updated in the worktree whose branch will carry the change. Session-local `.copilot/` state is
not a replacement for tracked guidance. Preserve unrelated user edits, and follow `.gitattributes`
merge rules for append-only Squad state.

After editing a source-owned file, report its exact path and validation. A session's file change
is not merged source-repository state until the branch is integrated into the intended base.

## Explicit handoffs and sequencing

Every handoff names:

- source and destination session/worktree;
- branch and PR (if any);
- changed paths and validation results;
- upstream/downstream dependencies;
- unresolved risks and the next safe action.

Run independent work in parallel. For stacked work, identify the upstream branch/PR, wait for
the upstream state to be available, then update and validate the dependent before merge. In this
repository, the normal base and merge target is `main`; do not assume a `dev` or `insiders`
branch.

## Recovery

For an interrupted session, locate its session record and reported worktree, then inspect status,
diff, branch, and recent history before taking action. Preserve uncommitted edits. Resume in
that worktree when ownership is clear; otherwise hand off the exact state to the coordinator.
Only prune stale worktree metadata after confirming no live session or recoverable changes depend
on it.

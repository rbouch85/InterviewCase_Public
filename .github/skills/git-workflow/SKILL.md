---
name: "git-workflow"
description: "Safe main-based branching, worktrees, and PR sequencing for InterviewCase_Public"
domain: "version-control"
confidence: "high"
source: "repository"
---

## Repository topology

`main` is the canonical integration and release branch for this repository. Do not assume
`dev`, `insiders`, or a promotion pipeline exists. Issue and feature branches normally start
from `main` and target `main`, unless an explicitly documented stacked-PR dependency says
otherwise.

Use the repository's established branch naming convention when one is supplied by the
coordinator. Do not invent a branch or switch branches in a shared worktree without explicit
direction.

## Copilot App sessions and worktrees

Each Copilot App coding session may have its own checkout/worktree, branch, index, and
uncommitted changes. Navigate to the session/worktree reported by the App before inspecting
or editing its files. A change in one session is not present in another session or in the
source repository until it is handed off and integrated.

Keep source-repository resources in the source worktree:

- `.github/skills/**` is tracked repository guidance, not session-only state.
- Tracked `.squad/**` files are shared team state; preserve unrelated edits and use the
  repository's stated ownership/merge rules.
- `.copilot/` and other session-local artifacts are not substitutes for tracked resources.

An explicit handoff should name the worktree/session, branch or PR, changed paths, validation
performed, dependencies, and remaining risks. Do not claim that a session change is merged
until the source repository reflects it.

## Independent and stacked work

- Independent changes can use separate session worktrees and separate PRs targeting `main`.
- All parallel PR tasks MUST use isolated Copilot sessions/worktrees and distinct task
  branches. Never reuse a shared in-place checkout for concurrent work.
- Before creating a task branch, fetch the intended base and branch explicitly from its
  latest remote tip (normally `origin/main`), rather than from whatever commit happens
  to be checked out in the current worktree:
  ```bash
  git fetch origin main
  git worktree add ../{repo-name}-{task} -b {task-branch} origin/main
  ```
  For a stacked PR, substitute the explicitly named upstream branch/commit for
  `origin/main` and record that dependency.
- A dependent change may stack on an upstream branch/PR only when the dependency is explicit.
  Identify the upstream ref in the handoff and PR description.
- Merge or land upstream dependencies first; then rebase/update and validate dependents before
  merging them to `main`.
- Keep commits and PRs scoped to their stated change. Do not mix unrelated worktree cleanup or
  resource edits into a dependent PR.

## Safe lifecycle

1. Inspect status, branch, remotes, and existing worktree changes before acting.
2. Create or use an isolated worktree for parallel work; do not switch a shared checkout out
   from under another session.
3. Make and validate changes in that worktree. Commit, push, or create a PR only when explicitly
   requested.
4. Hand off exact state before another agent continues.
5. After merge or confirmed abandonment, remove only the empty/unneeded worktree and prune stale
   metadata. Never delete uncommitted or unhanded-off work.

When recovering an interrupted session, inspect session history and the worktree status first;
preserve recoverable edits, then resume or hand them off rather than resetting them.

## PR scope gates

Before every commit/push that will feed a PR, and again before opening or updating the PR:

1. Confirm the full branch scope against the intended base, not only the latest commit:
   ```bash
   git diff origin/main...HEAD --name-only
   ```
   For a stacked PR, replace `origin/main` with the explicitly recorded base ref.
2. Check patch and whitespace errors:
   ```bash
   git diff --check
   ```
3. Verify the changed-file list on GitHub after the branch is pushed (for example with
   `gh pr view {number} --json files`) and confirm it matches the intended base-to-head
   scope. Do not open or update the PR until unexpected files are removed or the base is
   corrected.

Latest-commit inspection is not a substitute for these gates: GitHub computes PR scope
from the complete base-to-head diff, so earlier commits can reappear when a branch starts
from the wrong checkout `HEAD`.

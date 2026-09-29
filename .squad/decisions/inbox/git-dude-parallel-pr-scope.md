### 2026-09-24: Isolate parallel PR work and verify full scope
**By:** Git-Dude
**What:** Concurrent PR work must use isolated Copilot sessions/worktrees and task branches
based explicitly on the intended latest base branch. Before push, PR open, or PR update,
check the complete base-to-head scope with `git diff origin/main...HEAD --name-only`,
run `git diff --check`, and verify the changed files reported by GitHub.
**Why:** PR #9 was created from a shared in-place checkout whose `HEAD` already contained
PR #8's commit. The latest Kaplan-Meier commit touched only six files, but GitHub correctly
computed the branch's full diff against `main`, so PR #8 changes reappeared. Dirty unrelated
files were not the root cause. Inspecting only the latest commit is insufficient because
PR scope is the complete base-to-head diff; isolated worktrees, explicit base selection, and
the scope gates prevent this recurrence.

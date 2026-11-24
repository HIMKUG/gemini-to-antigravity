# Task Handoff for Remote Execution

> **Example** — a filled-out `GEMINI_HANDOFF.md` for a bug-fix relay.
> Place this file at the root of the handoff ZIP, alongside the full source tree.

## Environment Notice
You are working on a complete snapshot of the project source code inside this ZIP. You do not have local build or compiler tools, so pay extra attention to imports, type signatures, dependency declarations, and cross-file symbol consistency.

## 1. User Original Request (Verbatim)
> The app crashes intermittently when the scheduler hits a paused task. Fix the retry logic so a paused task is skipped instead of retried, and make sure the crash cannot recur through the same path. Ship a release build afterwards.

## 2. Confirmed Issues & Local Context (Found by Local AI)
- `src/core/scheduler.ts:112-140`: `runNext()` dereferences `task.nextRunAt` without checking `task.status === 'paused'`. A paused task keeps a stale `nextRunAt` from before the pause, so the queue treats it as due and the retry loop calls `execute()` on a task whose `handler` was already disposed during pause. That is the null dereference in the attached stack trace.
- `src/core/retry.ts:40-58`: backoff is computed from `attempt` only; it ignores `task.status`, so every retry re-enters the same broken path.

## 3. Suspect Areas to Investigate
- `src/core/queue.ts`: the dequeue predicate may also lack a paused filter — check whether a paused task can re-enter via a second route.
- `src/state/taskStore.ts`: `dispose()` sets `handler = null` but does not clear the task from the live index; decide whether that leaves a dangling reference.
- `src/core/retry.ts` (beyond lines 40-58): check the jitter calculation for negative values when `attempt` is 0.

## 4. Deliverable & Return Contract
When finished, return a single ZIP archive containing:
1. The complete modified source tree preserving the exact relative directory structure of this archive.
2. A `CHANGE_REPORT.md` file at the ZIP root containing:
   - **Summary of Changes**: File-by-file list of what changed and why.
   - **Findings on Suspect Areas**: What you checked and whether any additional issues were fixed.
   - **Deleted Files**: Exact relative paths of any files you deleted (write `None` if no files were removed).
   - **Build & Dependency Notes**: Any new packages, imports, permissions, or build steps the local AI should verify.

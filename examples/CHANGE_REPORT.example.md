# CHANGE_REPORT.md

> **Example** — the report a remote AI returns alongside the modified source tree.
> A report missing any of the four sections below is an incomplete deliverable.

## Summary of Changes
- `src/core/scheduler.ts` — `runNext()` now filters `status === 'paused'` before the due check; a paused task is deferred, not executed.
- `src/core/retry.ts` — backoff entry point returns early for paused tasks; jitter is clamped to non-negative.
- `src/core/queue.ts` — dequeue predicate additionally excludes paused tasks, closing the second re-entry route.

## Findings on Suspect Areas
- `src/core/queue.ts` — **Confirmed.** Paused tasks could re-enter through `dequeueDue()` even after the scheduler fix. Added the same paused filter; covered by the existing queue test suite.
- `src/state/taskStore.ts` — **Audited, no change.** The live index entry is intentionally retained so a paused task can be resumed; `dispose()` nulling the handler is correct because `runNext()` now never reaches execution for paused tasks.
- `src/core/retry.ts` — **Confirmed.** Jitter at `attempt === 0` could go negative and produce a past `nextRunAt`, causing an immediate retry storm. Clamped with `Math.max(0, …)`.

## Deleted Files
None

## Build & Dependency Notes
- No new dependencies.
- No new imports across module boundaries — the paused filter is defined once in `src/core/taskStatus.ts` and imported by both `scheduler.ts` and `queue.ts`.
- No schema, permission, or build-config changes.
- Local verification to run: typecheck, unit tests for `scheduler`/`queue`/`retry`, then the release build.

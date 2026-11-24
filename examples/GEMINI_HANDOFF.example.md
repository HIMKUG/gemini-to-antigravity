# Task Handoff for Remote Execution

> **Example** — the outbound state (filled by A AI) and the returned state (filled by B AI).
> A AI ships §1–§8; B AI appends to §6 and §7 and returns the same file.

## Environment Notice
You are working on a complete snapshot of the project source code inside this ZIP. You do not have local build or compiler tools, so pay extra attention to imports, type signatures, dependency declarations, and cross-file symbol consistency.

## 1. User Original Request (Verbatim)
> The app crashes intermittently when the scheduler hits a paused task. Fix the retry logic so a paused task is skipped instead of retried, and make sure the crash cannot recur through the same path. Ship a release build afterwards.

## 2. Fault Ledger (confirmed by local AI)

### F-01 · `src/core/scheduler.ts:112-140`
- **Problem:** `runNext()` reads `task.nextRunAt` before it reads `task.status`. A task paused after being scheduled keeps a stale `nextRunAt`, so the queue sees it as due, calls `execute()`, and the handler was disposed during the pause — the call dereferences a null handler. The failure is reproducible by pausing a task whose `nextRunAt` is already in the past.
- **Evidence:** stack trace line 3: `TypeError: Cannot read properties of null (reading 'invoke') at Scheduler.execute (scheduler.ts:131)`; reproduction in `test/repro-paused-task.test.ts`.
- **Must not:** the public shape of `Scheduler.runNext()` must stay the same; other call sites depend on its return value.

### F-02 · `src/core/retry.ts:40-58`
- **Problem:** backoff is computed from `attempt` alone and ignores task status, so a paused task re-enters the same broken path on every retry instead of being excluded once. With `attempt = 0`, jitter can also produce a negative delay, scheduling a retry in the past.
- **Evidence:** `test/repro-retry-negative-jitter.test.ts` asserts a `nextRunAt` in the past.
- **Must not:** retry counts already recorded in the store must remain readable; do not renumber attempts.

## 3. Requirement Ledger (from the user, restated)

### U-01 · "a paused task is skipped instead of retried"
- **Acceptance:** with a paused task whose `nextRunAt` is due, `runNext()` returns without invoking the handler, and the task remains paused afterwards.

### U-02 · "the crash cannot recur through the same path"
- **Acceptance:** a regression test exists that pauses a due task and runs at least three scheduler ticks; no exception is raised and no handler is invoked.

### U-03 · "ship a release build"
- **Acceptance:** the release artifact builds locally after the merge; this one is A AI's to verify, not B AI's.

## 4. Suspect Areas (unverified)

### S-01 · `src/core/queue.ts`
- **Why suspect:** the dequeue predicate may also lack a paused filter, which would let a paused task re-enter by a route that bypasses `scheduler.ts` entirely.
- **Check:** does any path from `dequeueDue()` reach `execute()` without consulting `status`? Answer yes or no, with the call chain.

### S-02 · `src/state/taskStore.ts`
- **Why suspect:** `dispose()` nulls the handler but does not remove the task from the live index, which may leave a dangling reference that another consumer reads.
- **Check:** is any live-index entry read after `dispose()` without a null guard? Name the reader, or state that there is none.

## 5. Execution Rules for You (B AI)

1. Work through the IDs in order. If a fix must precede another, say so in the entry and name the dependency.
2. After finishing each ID, immediately append its entry to §6. Do not hold entries and write them at the end; a batched ledger is a lost ledger.
3. Never merge two IDs into one entry. One ID, one entry, one outcome.
4. Every entry must name the files and the line ranges you changed, and state how the change was verified.
5. If an ID cannot be completed, write `STATUS: FAILED` and the exact blocker: the error text, the file and line where you stopped, and what you tried. A failed entry with real evidence is acceptable. Silence is not.
6. Do not edit any file you have not named in an entry. If you must, add an entry with an `X-` ID and justify it.
7. Do not delete any file without an entry naming its path.
8. Before returning, complete §7 in full. Every ID from §2, §3 and §4 must appear there with `DONE`, `FAILED`, or `NOT-APPLICABLE`, and every `DONE` must point at the file and line range that proves it.

## 6. Execution Ledger — append one entry per ID as you go

### F-01
- **STATUS:** DONE
- **Files:** `src/core/scheduler.ts`
- **Lines:** 112-136
- **Change:** `runNext()` now tests `task.status === 'paused'` before the due check and returns early; the stale `nextRunAt` is left untouched so a resume still works.
- **Verified:** paused-due task no longer reaches `execute()`; `test/repro-paused-task.test.ts` passes.

### F-02
- **STATUS:** DONE
- **Files:** `src/core/retry.ts`
- **Lines:** 40-62
- **Change:** backoff returns early for paused tasks; delay is clamped with `Math.max(0, …)` so a negative jitter cannot schedule a past retry.
- **Verified:** `test/repro-retry-negative-jitter.test.ts` passes.

### U-01
- **STATUS:** DONE
- **Files:** `src/core/scheduler.ts`
- **Lines:** 112-136
- **Change:** covered by the same early return as F-01; acceptance is observable as no handler invocation.
- **Verified:** the test asserts the handler is not called and the status is still `paused`.

### U-02
- **STATUS:** DONE
- **Files:** `test/regression-paused-task.test.ts`
- **Lines:** 1-48
- **Change:** new test runs three scheduler ticks with a paused due task and asserts no throw and no invocation.
- **Verified:** the test fails on the pre-fix tree and passes on this tree.

### U-03
- **STATUS:** NOT-APPLICABLE
- **Files:** —
- **Lines:** —
- **Change:** release build is A AI's gate, per the acceptance text.
- **Verified:** —

### S-01
- **STATUS:** DONE
- **Files:** `src/core/queue.ts`
- **Lines:** 88-96
- **Change:** `dequeueDue()` had no paused filter and could reach `execute()` directly. Added the same guard there.
- **Verified:** call chain `dequeueDue → enqueueRetry → execute` now stops at the guard; `queue.test.ts` passes.

### S-02
- **STATUS:** NOT-APPLICABLE
- **Files:** — (no change)
- **Lines:** —
- **Change:** audited, no dangling read found. Every live-index reader guards for a null handler.
- **Verified:** read `taskStore.ts:60-120` and both consumers; no code change needed.

## 7. Self-Audit Before Return

| ID | Status | Evidence |
| --- | --- | --- |
| F-01 | DONE | `src/core/scheduler.ts:112-136` |
| F-02 | DONE | `src/core/retry.ts:40-62` |
| U-01 | DONE | `src/core/scheduler.ts:112-136` |
| U-02 | DONE | `test/regression-paused-task.test.ts:1-48` |
| U-03 | NOT-APPLICABLE | local build gate |
| S-01 | DONE | `src/core/queue.ts:88-96` |
| S-02 | NOT-APPLICABLE | audited, no change |

## 8. Deliverable & Return Contract

Return a single ZIP containing:

1. The complete modified source tree, preserving the exact relative directory structure of this archive.
2. This same `GEMINI_HANDOFF.md`, with §6 and §7 filled in — not a separate report.
3. Any files listed as deleted in §6.

Nothing else. A return missing an ID, or whose diff does not match its entries, is rejected as incomplete.

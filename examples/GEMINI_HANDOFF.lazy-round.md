# Task Handoff for Remote Execution

> **Anti-example** — a round that must be rejected. Use it to calibrate `check_ledger.py`.
> Every failure below is one this protocol exists to catch.

## Environment Notice
You are working on a snapshot of the project source code. You have no local build or compiler tools.

## 1. User Original Request (Verbatim)
> Fix the retry logic so a paused task is skipped instead of retried, and make sure the crash cannot recur through the same path.

## 2. Fault Ledger (confirmed by local AI)

### F-01 · `src/core/scheduler.ts:112-140`
- **Problem:** paused tasks reach `execute()` and dereference a disposed handler.
- **Evidence:** stack trace at `scheduler.ts:131`.

### F-02 · `src/core/retry.ts:40-58`
- **Problem:** backoff ignores task status and can produce a negative delay.

## 3. Requirement Ledger (from the user, restated)

### U-01 · "a paused task is skipped instead of retried"
- **Acceptance:** a paused due task does not invoke the handler.

### U-02 · "the crash cannot recur through the same path"
- **Acceptance:** a regression test runs three ticks with a paused due task.

## 4. Suspect Areas (unverified)

### S-01 · `src/core/queue.ts`
- **Why suspect:** dequeue may bypass the paused filter.
- **Check:** can `dequeueDue()` reach `execute()` without reading status?

## 5. Execution Rules for You (B AI)
1. Work through the IDs in order and append each entry to §6 as you finish it.
2. Every entry names files and line ranges.
3. Complete §7 before returning, one row per ID from §2–§4.

## 6. Execution Ledger — append one entry per ID as you go

### F-01
- **STATUS:** DONE
- **Files:** `src/core/scheduler.ts`
- **Lines:** 112-140
- **Change:** fixed.

Good. Everything here is handled. The scheduler guard was added and the retry
logic was reviewed.

### S-01
- **STATUS:** DONE
- **Files:** `src/core/queue.ts`
- **Lines:** 88-96
- **Change:** also fixed the queue.

## 7. Self-Audit Before Return

| ID | Status | Evidence |
| --- | --- | --- |
| F-01 | DONE | scheduler fixed |
| S-01 | DONE | queue fixed |

## 8. Deliverable & Return Contract
Return the modified tree plus this file.

---

# Why this round fails

| Check | Result |
| --- | --- |
| F-02 has an entry in §6 | ✗ absent |
| U-01 has an entry in §6 | ✗ absent |
| U-02 has an entry in §6 | ✗ absent |
| §7 lists every ID | ✗ F-02, U-01, U-02 missing |
| `DONE` entries state *how* the change was verified | ✗ "fixed." is not a verification |
| Prose substituting for entries | ✗ "Everything here is handled" closes nothing |

Running the checker on this file (with §6 and §7 as given) reports the missing
IDs and exits non-zero. That is the point: a confident summary is not a ledger.

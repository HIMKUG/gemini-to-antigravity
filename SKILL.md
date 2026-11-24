---
name: gemini-to-antigravity
description: Orchestrate asynchronous two-AI code collaboration between a local agent with Git and a build toolchain (A AI / Antigravity) and an unlimited-quota remote model with no local environment (B AI / Gemini). Use when delegating heavy code changes through a maximum-compression source ZIP plus a self-contained handoff ledger, or when receiving a modified ZIP back to verify the ledger against git diff, audit every item ID, build release artifacts, and triage compile errors locally.
license: MIT
---

# Gemini to Antigravity

Coordinate a two-AI relay where the local AI (**A AI** — holds Git, the compiler, and the release gate) acts as diagnostician, reviewer, and builder, while the remote AI (**B AI** — unlimited quota, no toolchain) executes heavy code changes.

The handoff document is not a description. It is a **ledger**: numbered items that B AI must close one by one, writing an entry for each as it goes, then auditing all of them before returning. A AI verifies the ledger against `git diff`.

## When to Use

* **Outbound (A AI → B AI)**: the user asks to package a project for Gemini, hand off a task/bug/feature, or prepare a handoff ZIP.
* **Inbound (B AI → A AI)**: the user returns a modified ZIP and asks to apply it, review diffs, compile, build, or fix build errors.
* **Rework**: the returned round failed review or build and must go back.

## The Ledger Model

Three ID namespaces, assigned by A AI, never reused, never renumbered:

| Prefix | Meaning | Required fields |
| --- | --- | --- |
| `F-nn` | **Confirmed fault** — reproduced or verified locally | locator, problem statement, evidence |
| `U-nn` | **User requirement** — restated from the verbatim request as a checkable outcome | verbatim quote, acceptance test |
| `S-nn` | **Suspect area** — unverified; B AI must audit and report findings | locator, why it is suspect |

B AI answers every ID in §6 of the handoff, and audits every ID in §7 before returning. An ID with no entry is an incomplete round. An entry with no matching diff is a false claim.

---

## Phase 1: Outbound Delegation (A AI → B AI)

### 1. Local Pre-Diagnosis

Read the request verbatim and preserve it byte-for-byte. Then inspect the repository and classify what you find into `F`, `U`, and `S`. Do not write the prompt until you can place every finding into one of the three.

### 2. Writing the Handoff — the Five Rules

A handoff is "precise" when B AI cannot act without understanding. These rules enforce that.

**Rule 1 — Locate or downgrade.** Every `F-nn` begins with a locator.
- Line range known → `path/to/file.ext:112-140`
- Only the first line known → `path/to/file.ext:112`
- Line unknown, file known → `path/to/file.ext`
- Neither known → it is **not** a confirmed fault. It goes to `S-nn`, never to `F-nn`.

**Rule 2 — State the problem, never the remedy.** Describe what the code does now, what it must do instead, which input triggers the failure, and what the failure looks like. Write no patch, no suggested API, no "change X to Y", no sketch of the fix.

Rationale: a remedy anchors B AI to A AI's first guess and hides whether B AI actually understood the fault. Stating only the problem forces B AI to derive a fix, and lets A AI review the result against a criterion that was fixed before the work started.

**Rule 3 — Restate the user as verifiable items.** §1 holds the request verbatim and is never edited. §3 turns each sentence of it into `U-nn` with an observable acceptance test: "a paused task is skipped, not retried", not "fix the bug".

**Rule 4 — Never blur confirmed with suspected.** `F-nn` means reproduced. `S-nn` means a hypothesis. B AI treats them differently: `F` must be fixed, `S` must be investigated and reported even when the answer is "nothing wrong here".

**Rule 5 — One fault per ID.** Two symptoms in one entry means one of them gets fixed and the other silently survives.

### 3. Handoff File Structure (`GEMINI_HANDOFF.md`, at the ZIP root)

```
# Task Handoff for Remote Execution

## Environment Notice
...

## 1. User Original Request (Verbatim)
> <the user's exact words, unmodified>

## 2. Fault Ledger (confirmed by local AI)
### F-01 · `src/core/scheduler.ts:112-140`
- **Problem:** <what the code does now, what it must do, which input triggers it, what breaks>
- **Evidence:** <stack trace line, log line, reproduction command, or the assertion that failed>
- **Must not:** <any boundary B AI could cross while fixing — a contract, a public API, a performance budget>

## 3. Requirement Ledger (from the user, restated)
### U-01 · "<verbatim fragment>"
- **Acceptance:** <an observable outcome A AI can check in the diff or in a test>

## 4. Suspect Areas (unverified)
### S-01 · `src/core/queue.ts`
- **Why suspect:** <the coupling or invariant that made you distrust it>
- **Check:** <the specific question B AI must answer, even if the answer is "clean">

## 5. Execution Rules for You (B AI)
<the eight rules below, verbatim>

## 6. Execution Ledger — append one entry per ID as you go
<template and an empty instruction line>

## 7. Self-Audit Before Return
<the audit table and its completion rules>

## 8. Deliverable & Return Contract
<the exact ZIP shape>
```

### 4. §5 — the execution rules, written into the handoff

```
1. Work through the IDs in order. If a fix must precede another, say so in the
   entry and name the dependency.
2. After finishing each ID, immediately append its entry to §6. Do not hold
   entries and write them at the end; a batched ledger is a lost ledger.
3. Never merge two IDs into one entry. One ID, one entry, one outcome.
4. Every entry must name the files and the line ranges you changed, and state
   how the change was verified.
5. If an ID cannot be completed, write STATUS: FAILED and the exact blocker:
   the error text, the file and line where you stopped, and what you tried.
   A failed entry with real evidence is acceptable. Silence is not.
6. Do not edit any file you have not named in an entry. If you must, add an
   entry with a new ID, prefixed X-, and justify it.
7. Do not delete any file without an entry naming its path.
8. Before returning, complete §7 in full. Every ID from §2, §3 and §4 must
   appear there with DONE, FAILED, or NOT-APPLICABLE, and every DONE must
   point at the file and line range that proves it.
```

### 5. Package with Maximum Compression

Pack `GEMINI_HANDOFF.md` with the complete clean source tree, DEFLATE level 9 (`zipfile.ZIP_DEFLATED`, `compresslevel=9`, or `zip -9 -r`).

Exclude `.git/` and generated or cached directories: `node_modules/`, `target/`, `build/`, `dist/`, `.gradle/`, `.dart_tool/`, `__pycache__/`, `.venv/`, `.idea/`, `.vs/`, `.DS_Store`, plus any file holding a secret. Respect `.gitignore` for build artifacts while keeping every file the task needs.

Verify the archive: `GEMINI_HANDOFF.md` at the root, relative layout preserved, no `.env`/key material inside. Report the exact path and size.

---

## Phase 2: Inbound Integration, Review & Build (B AI → A AI)

### 1. Git Safety Checkpoint

Run `git status`. If the tree is dirty, commit or create a named stash before anything else, so the pre-overwrite state is always recoverable.

### 2. Staged Extraction

Extract into a temporary staging directory. Never extract over the working tree.

* Detect a wrapper folder (the returned tree often sits inside `project_name/`) and normalize the source root.
* Read the returned `GEMINI_HANDOFF.md` §6 and §7 in full before copying a single source file.
* Overwrite only files present in the returned tree.
* Apply deletions only where §6 names the path.
* Keep `GEMINI_HANDOFF.md` out of the repository; it is a working artifact, not a deliverable.

### 3. Ledger Verification — mechanical, before review

Run the completeness check before reading any diff, so a lazy round fails fast:

```bash
python scripts/check_ledger.py returned/GEMINI_HANDOFF.md
```

It extracts every ID from §2–§4 and asserts each one appears in §6 with a status, and again in §7 with a status. Missing IDs, duplicate entries, or a `DONE` with no `Files:`/`Lines:` fields exit non-zero.

Then verify claims against evidence:

* Each `DONE` entry names files and line ranges — confirm the diff actually touches those ranges.
* Each `Failed` entry is specific: error text, stopping point, attempt made.
* Any file in the diff that no entry names is drift; report it before proceeding.

### 4. Git Diff Review

The ledger is a claim; the diff is the evidence.

* `git status` and `git diff --stat` for the blast radius.
* Full `git diff` for intent — read it, do not skim it.
* Cross-check against §2 (the faults), §3 (the acceptance tests), and the verbatim request.
* Hunt for truncation, reformat noise, out-of-scope edits, and silent deletions.

### 5. Local Compile & Release Build

B AI has no toolchain, so the build gate is A AI's. Run typecheck, compile, tests, then build the artifact the user asked for.

### 6. Error Triage

* **Mechanical** (missing import, forgotten dependency, syntax typo, visibility mismatch) — fix locally, rebuild, ship. Never spend a relay round on this.
* **Structural** (a `F-nn` not fixed, a `U-nn` unmet, a `S-nn` not audited, an entry that contradicts the diff, or a build failure that reveals a design defect) — reject the round and send a rework.

### 7. The Rework Round — append the death record

Never overwrite the previous round. Append to the same file:

```
## 9. Round <n> — Death Record (written by A AI)

### Claims that failed
- F-01: §6 says DONE at `scheduler.ts:112-140`. `git diff` shows no change in
  that range. The claim is not in the diff.
- F-03: no entry at all. Not attempted.

### Build evidence
<verbatim compiler output, trimmed to the failing lines>

### Drift
<files changed without an entry, with the line ranges>

### What to do this round
Re-open only the IDs above; keep the entries you already wrote; append new
entries for the rework. Do not restate the whole tree.
```

B AI now reads its own failure, one ID at a time, in the same document it must keep appending to. This is the intended pressure: a lazily finished round costs a full document of its own mistakes.

### 8. Final Delivery Summary

Report to the user: which IDs closed, grounded in `git diff`; the mechanical fixes applied locally; the verification status; the exact path of the release artifact.

---

## Gotchas

* **Never assume B AI knows the protocol.** Every rule it must follow lives inside the handoff file. A rule that is not written there does not exist.
* **Never write the remedy.** The moment A AI sketches the fix, the review stops being independent — A AI starts grading its own idea.
* **A batched ledger is a lie with better formatting.** If entries arrive all at once at the end, the work was probably not done in order; check the diff harder.
* **Wrapper folders are the default.** Inspect the staging tree before overwriting anything.
* **Do not bounce mechanical errors.** A missing import costs seconds locally and an entire relay round remotely.
* **A failed entry is a good entry.** B AI reporting "could not do F-03, blocker at line 88, error text attached" is a usable outcome; an empty round is not.

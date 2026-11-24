# The Gemini–Antigravity Protocol

This document states the relay as explicit invariants, so any pair of agents — not just the ones in this repo's examples — can implement it and be checked against it.

## Roles

| Role | Holds | Must not |
| --- | --- | --- |
| **A AI** (local) | Repository, `git`, build/compile/package toolchain, release authority | Delegate a verification it can perform itself |
| **B AI** (remote) | Unlimited compute quota, ZIP read/write, no toolchain | Assume knowledge of the repo, the protocol, or earlier context |

The asymmetry is intentional: quota lives remotely, truth lives locally.

## The ledger

The handoff document is a ledger, not a description. It carries numbered items in three namespaces, assigned by A AI, never reused, never renumbered.

| Prefix | Meaning | Declared in | Required fields |
| --- | --- | --- | --- |
| `F-nn` | Confirmed fault, reproduced locally | §2 | locator, problem, evidence, must-not |
| `U-nn` | User requirement, restated as a checkable outcome | §3 | verbatim fragment, acceptance test |
| `S-nn` | Suspect area, unverified | §4 | locator, why suspect, what to check |
| `X-nn` | Out-of-scope change declared by B AI | §6 | justification |

### Locator grammar

Every `F-nn` and `S-nn` heading ends with a locator, in the most specific form available:

```
### F-01 · src/core/scheduler.ts:112-140     line range known
### F-02 · src/core/scheduler.ts:131          single line known
### F-03 · src/core/scheduler.ts              file known, line unknown
```

No locator means no fault entry. A finding that cannot be located is a hypothesis and must be filed as `S-nn`.

### Problem statement, not remedy

An `F-nn` states: what the code does now, what it must do, which input triggers the failure, and what the failure looks like. It states no patch, no target API, no "change this to that", and no sketch of a solution.

Rationale: a stated remedy anchors B AI to A AI's first guess and hides whether B AI understood the fault. A stated problem forces derivation, and lets A AI review against a criterion frozen before the work started.

### Verified versus suspected

`F-nn` means reproduced. `S-nn` means a hypothesis. B AI must fix every `F`, and must answer every `S` — including with "audited, nothing wrong, no change" (`NOT-APPLICABLE`). A suspect that was never mentioned during the round is an incomplete round.

## Artifacts

### `GEMINI_HANDOFF.md` — outbound half

Written by A AI; placed at the archive root. Sections:

| § | Content | Filled by |
| --- | --- | --- |
| 1 | User request, verbatim, never edited | A AI |
| 2 | Fault ledger (`F-nn`) | A AI |
| 3 | Requirement ledger (`U-nn`) | A AI |
| 4 | Suspect areas (`S-nn`) | A AI |
| 5 | Execution rules for B AI, verbatim | A AI |
| 6 | Execution ledger — one entry per ID, appended as work proceeds | B AI |
| 7 | Self-audit table — one row per ID | B AI |
| 8 | Deliverable and return contract | A AI |
| 9 | Round death record (rework rounds only) | A AI |

### `GEMINI_HANDOFF.md` — returned half

B AI returns the **same file**, with §6 and §7 filled. It does not write a separate report: a separate report is a place where entries can be summarized instead of written, and summaries are where laziness hides.

An entry in §6:

```markdown
### F-01
- **STATUS:** DONE | FAILED | NOT-APPLICABLE
- **Files:** path or paths touched
- **Lines:** line range in each file
- **Change:** what was changed and why, in one or two sentences
- **Verified:** how the change was confirmed — command, test, or reasoning
```

A `FAILED` entry replaces `Change`/`Verified` with:

```markdown
- **Blocker:** the exact error text or the unmet precondition
- **Stopped at:** file and line where work stopped
- **Tried:** what was attempted
```

A failed entry with real evidence is a complete entry. Silence is not.

### Handoff archive

- Compression: DEFLATE level 9 (`zipfile.ZIP_DEFLATED`, `compresslevel=9`, or `zip -9`).
- Root layout: `GEMINI_HANDOFF.md` at the archive root, then the relative source tree.
- Exclusions: `.git/`, build outputs, package caches, IDE directories, and secret-bearing files. A AI MUST verify no secret file entered the archive.

## State machine

```
IDLE
  └─▶ DIAGNOSING        A AI reads source/logs; assigns F, U, S with locators
        └─▶ PACKING     A AI writes §1-§8, packs ZIP -9, verifies root + secrets
              └─▶ REMOTE_BUSY
                    └─▶ CHECKPOINT     A AI: git status; commit or named stash
                          └─▶ STAGING  A AI: extract to temp, normalize wrapper
                                └─▶ LEDGER_CHECK  check_ledger.py: all IDs present
                                      ├─ fail ─▶ REWORK (§9 appended)
                                      └─ pass ─▶ MERGING   overwrite sources
                                            └─▶ REVIEWING   git diff vs §2/§3/§4
                                                  ├─ pass ─▶ BUILDING
                                                  │            ├─ clean ─▶ DELIVERED
                                                  │            └─ mechanical ─▶ PATCHING ─▶ BUILDING
                                                  └─ fail ─▶ REWORK (§9 appended)
```

Forbidden transitions:

- `REMOTE_BUSY → MERGING` without `CHECKPOINT`.
- `STAGING → MERGING` before §6 and §7 have been read in full.
- `LEDGER_CHECK → MERGING` with any missing or malformed ID.
- `REVIEWING → DELIVERED` without reading the full diff.
- `BUILDING → REWORK` for a mechanical error.

## Rework

A rework round appends §9 to the same file. It never rewrites §6: B AI's own entries stay, so the next round is judged against what B AI claimed last time.

§9 contains: the claims that failed, with the ID and what the diff actually shows; the build evidence, verbatim; the drift, meaning files changed that no entry names; and a scope line naming which IDs to re-open.

## Invariants

- **I1** No artifact contains credentials.
- **I2** The returned archive's relative layout is byte-identical to the handoff's.
- **I3** Every `F`, `U`, and `S` declared in §2–§4 has exactly one §6 entry and one §7 row.
- **I4** Every `DONE` names files and lines; every `FAILED` names a blocker and a stopping point.
- **I5** Every §7 status equals its §6 status.
- **I6** Every deletion is named in a §6 entry.
- **I7** Every file in the diff is named in a §6 entry.
- **I8** A `F-nn` entry contains no prescribed remedy written by A AI.
- **I9** Handoff files never enter version control.
- **I10** The pre-overwrite state is recoverable (commit or named stash).
- **I11** The release artifact is produced by the side that owns the toolchain.
- **I12** A rework is reserved for structural defects; mechanical defects are patched locally.

## Conformance checklist

- [ ] Every `F-nn` has a locator in the heading.
- [ ] Every `F-nn` states a problem and no remedy.
- [ ] Every `U-nn` carries a verbatim fragment and an observable acceptance test.
- [ ] Every `S-nn` states a specific question B AI must answer.
- [ ] §5 contains all eight execution rules verbatim.
- [ ] Archive is `-9`, handoff at root, layout preserved, no secrets.
- [ ] A checkpoint exists before any overwrite.
- [ ] `check_ledger.py` exits 0 on the returned file.
- [ ] Each `DONE` maps to real lines in `git diff`.
- [ ] The full diff was read, not just `--stat`.
- [ ] Typecheck, compile, and test ran locally.
- [ ] The release artifact path was reported to the user.

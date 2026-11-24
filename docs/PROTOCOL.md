# The Gemini–Antigravity Protocol

This document states the relay workflow as explicit invariants, so any pair of agents — not just the ones in this repo's examples — can implement it and be checked against it.

## Roles

| Role | Holds | Must not |
| --- | --- | --- |
| **A AI** (local) | Repository, `git`, build/compile/package toolchain, release authority | Delegate a verification it can perform itself |
| **B AI** (remote) | Unlimited compute quota, ZIP read/write, no toolchain | Assume knowledge of the repo, the skill, or earlier context |

The asymmetry is intentional: quota lives remotely, truth lives locally.

## Artifacts

The relay carries exactly two artifacts, and nothing else.

### `GEMINI_HANDOFF.md`

Written by A AI, placed at the archive root, consumed by B AI. It MUST contain all five sections:

1. **Environment Notice** — states that B AI has no compiler and must reason statically about imports, types, and cross-file symbols.
2. **User Original Request (Verbatim)** — the user's words, unmodified.
3. **Confirmed Issues** — each entry carries a file path and line range, verified locally.
4. **Suspect Areas** — named blind spots with a reason each.
5. **Deliverable & Return Contract** — the exact archive shape and the exact report schema.

Rationale: B AI starts with zero shared context. Anything not written into this file does not exist for it.

### Handoff archive

- Compression: DEFLATE level 9 (`zipfile.ZIP_DEFLATED`, `compresslevel=9`, or `zip -9`).
- Root layout: `GEMINI_HANDOFF.md` at the archive root, then the relative source tree.
- Exclusions: `.git/`, build outputs, package caches, IDE directories, and secret-bearing files. A AI MUST verify no secret file entered the archive.

### `CHANGE_REPORT.md`

Written by B AI, at the root of the returned archive. It MUST contain all four sections:

| Section | Content | Omission means |
| --- | --- | --- |
| Summary of Changes | File-by-file, what changed and why | Undocumented mutation |
| Findings on Suspect Areas | What was checked, found, fixed | Unanswered audit |
| Deleted Files | Relative paths, or the literal `None` | Unauthorized deletion |
| Build & Dependency Notes | New packages, imports, permissions, build steps | Unverified integration risk |

## State machine

```
IDLE
  └─▶ DIAGNOSING        A AI reads source/logs, splits confirmed vs suspect
        └─▶ PACKING     A AI writes handoff, packs ZIP -9, verifies root layout
              └─▶ REMOTE_BUSY
                    └─▶ CHECKPOINT     A AI: git status; commit or named stash
                          └─▶ STAGING  A AI: extract to temp, normalize wrapper
                                └─▶ MERGING   overwrite sources; apply deletions
                                      └─▶ REVIEWING   git diff vs report vs request
                                            ├─ pass ─▶ BUILDING   typecheck, compile, test, package
                                            │            ├─ clean ─▶ DELIVERED
                                            │            └─ mechanical ─▶ PATCHING ─▶ BUILDING
                                            └─ fail ─▶ REWORK  new handoff with logs + diff excerpts
```

Transitions that are forbidden:

- `REMOTE_BUSY → MERGING` without `CHECKPOINT`.
- `STAGING → MERGING` without reading `CHANGE_REPORT.md` in full.
- `REVIEWING → DELIVERED` without a non-empty `git diff` assessment.
- `BUILDING → REWORK` for a mechanical error (missing import, typo, forgotten dependency).

## Invariants

- **I1** No artifact contains credentials.
- **I2** The returned archive's relative layout is byte-identical to the handoff's.
- **I3** Every deletion appears in `Deleted Files`.
- **I4** Handoff files never enter version control.
- **I5** The pre-overwrite state is recoverable (`commit` or named `stash`).
- **I6** The release artifact is produced by the side that owns the toolchain.
- **I7** A rework round is reserved for structural defects; mechanical defects are patched locally.

## Failure catalogue

| Signal | Likely cause | Resolution |
| --- | --- | --- |
| Files one level too deep | Wrapper folder in returned ZIP | Normalize root during staging |
| Diff touches out-of-scope files | Model drifted from the request | Review rejection → rework with scope restated |
| Report lists deletions absent from diff | Report/diff mismatch | Trust the diff; ask for a corrected report |
| Compile fails on a symbol B AI never edited | Stale snapshot or missing file inclusion | Compare archive file list against repo |
| Handoff ZIP unexpectedly large | Binary assets or cache dirs leaked | Re-check denylist; consider manifest for media |

## Conformance checklist

A relay round is conformant when all of the following hold:

- [ ] Handoff contains all five sections, with the request verbatim.
- [ ] Archive is `-9`, excludes `.git` and caches, and has the handoff at root.
- [ ] A secret scan of the archive returns nothing.
- [ ] A checkpoint exists before any overwrite.
- [ ] Report contains all four sections.
- [ ] `git diff` was read in full, not merely `--stat`.
- [ ] Typecheck, compile, and test ran locally.
- [ ] The release artifact path was reported back to the user.

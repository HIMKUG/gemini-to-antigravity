---
name: gemini-to-antigravity
description: Orchestrate asynchronous two-AI code collaboration between a local agent with Git and a build toolchain (A AI / Antigravity) and an unlimited-quota remote model with no local environment (B AI / Gemini). Use when delegating heavy code changes through a maximum-compression source ZIP plus a self-contained handoff prompt, or when receiving a modified ZIP back to overwrite a Git repo, review the diff, build release artifacts, and triage compile errors locally.
license: MIT
---

# Gemini to Antigravity

Coordinate a two-AI relay workflow where the local AI (A AI, with Git and build/compile tools) acts as commander, diagnostician, reviewer, and builder, while the remote AI (B AI, with unlimited quota and ZIP tools but no local build environment) executes heavy code changes.

## When to Use

Use this skill in either phase of the relay workflow:

* **Outbound (Delegate to B AI)**: The user asks to package the project for Gemini, hand off a task/bug/feature to the remote AI, or prepare a handoff ZIP.

* **Inbound (Merge & Build from B AI)**: The user returns a modified ZIP from Gemini and asks to apply the changes, review diffs, compile, build a release executable or APK, or fix build errors.

## Phase 1: Outbound Delegation (A AI to B AI)

### 1. Local Pre-Diagnosis

Before writing the handoff prompt, inspect the local repository to give B AI a head start and avoid wasted rounds:

* Read the user's request carefully and preserve it verbatim.

* Locate relevant source files, error logs, stack traces, or architectural constraints related to the request.

* Separate **Confirmed Issues** (verified with file paths and line numbers) from **Suspect Areas** (places you suspect might also have bugs, edge cases, or coupling issues that B AI should audit).

### 2. Write a Self-Contained Handoff Prompt (`GEMINI_HANDOFF.md`)

B AI does not know this skill and has no local environment. Write `GEMINI_HANDOFF.md` at the root of the ZIP so B AI immediately understands the mission, constraints, and return format. Use this structure:

```
# Task Handoff for Remote Execution

## Environment Notice
You are working on a complete snapshot of the project source code inside this ZIP. You do not have local build or compiler tools, so pay extra attention to imports, type signatures, dependency declarations, and cross-file symbol consistency.

## 1. User Original Request (Verbatim)
<Paste the user's exact request here>

## 2. Confirmed Issues & Local Context (Found by Local AI)
- <File path + line range>: <Concrete issue, root cause, or constraint>

## 3. Suspect Areas to Investigate
- <File path or module>: <Why this area is suspect and what to check>

## 4. Deliverable & Return Contract
When finished, return a single ZIP archive containing:
1. The complete modified source tree preserving the exact relative directory structure of this archive.
2. A `CHANGE_REPORT.md` file at the ZIP root containing:
   - **Summary of Changes**: File-by-file list of what changed and why.
   - **Findings on Suspect Areas**: What you checked and whether any additional issues were fixed.
   - **Deleted Files**: Exact relative paths of any files you deleted (write `None` if no files were removed).
   - **Build & Dependency Notes**: Any new packages, imports, permissions, or build steps the local AI should verify.

```

### 3. Package Source Code with Maximum Compression

Pack `GEMINI_HANDOFF.md` together with the complete clean source tree into a ZIP using maximum compression (deflate level 9):

* Exclude `.git/` and heavy generated or cached directories so the archive stays small and clean: `node_modules/`, `target/`, `build/`, `dist/`, `.gradle/`, `.dart_tool/`, `__pycache__/`, `.venv/`, `.idea/`, `.vs/`, and `.DS_Store`. Respect `.gitignore` for build artifacts while ensuring all required source and config files are included.

* Prefer Python's `zipfile` with `compression=zipfile.ZIP_DEFLATED, compresslevel=9` (cross-platform) or `zip -9 -r` when available.

* Verify the resulting ZIP contains `GEMINI_HANDOFF.md` at its root and preserves the repository's relative directory layout.

* Report the exact output ZIP path and file size to the user so they can manually pass it to B AI.

## Phase 2: Inbound Integration, Review & Build (B AI to A AI)

### 1. Create a Git Safety Checkpoint

Before overwriting any file in the local repository:

* Run `git status`.

* If there are uncommitted changes, save a clean recovery point first (either commit them to the current branch or create a named stash/checkpoint) so the pre-overwrite state can always be restored cleanly.

### 2. Staged Extraction & Controlled Overwrite

Never blindly extract directly into the repository root without inspecting the archive layout:

* Extract B AI's returned ZIP into a temporary staging directory first.

* Check whether the archive wraps everything inside a single top-level folder (for example, `project_name/`) and normalize the source root accordingly.

* Read `CHANGE_REPORT.md` (or any summary file returned by B AI) in full.

* Copy and overwrite all modified source files into the local Git directory. Do not copy `GEMINI_HANDOFF.md` or `CHANGE_REPORT.md` into tracked repo files.

* Delete any local files explicitly listed under `Deleted Files` in `CHANGE_REPORT.md`.

* Remove the temporary staging directory after copying.

### 3. Review Changes via Git Diff

Use Git to verify what B AI actually changed instead of trusting the report blindly:

* Run `git status` and `git diff --stat`, then inspect `git diff` across modified files.

* Cross-check the diff against `CHANGE_REPORT.md` and the original user request.

* Check for accidental file truncations, broken formatting, or unintended edits outside the task scope.

### 4. Local Compile & Release Build Verification

Because B AI has no build toolchain, always verify compilation and packaging locally:

* Run the project's typecheck, compiler, and test commands.

* Build the target release artifact requested by the user (such as a release executable, installer, or Android APK).

### 5. Error Triage: Local Fix vs. Rework Delegation

Decide how to handle issues based on severity:

* **Small or Mechanical Errors (Fix Locally)**: Missing imports, forgotten library or dependency declarations, minor syntax/type typos, or small visibility/signature mismatches. Fix these directly in the local workspace, re-run the build, and verify the release artifact succeeds. Do not ask B AI to rework minor issues.

* **Major Logic Flaws or Review Failure (Reject & Rework)**: Rare, but if the `git diff` review fails, core requirements were missed, or compilation reveals severe architectural or logic defects, stop local patching. Immediately document the exact failures, compiler logs, and relevant diff excerpts in a new rework `GEMINI_HANDOFF.md`, repackage at maximum compression, and hand it back to B AI for a rework round.

### 6. Final Delivery Summary

Report back to the user concisely:

* Summary of accepted changes from B AI (grounded in `git diff`).

* Any local compile/import fixes you applied.

* Verification status and exact path of the built release executable or APK.

## Gotchas

* **Never assume B AI knows this workflow**: Every rule B AI must follow (directory structure, `CHANGE_REPORT.md`, `Deleted Files`) must live inside `GEMINI_HANDOFF.md`.

* **Watch for wrapper folders on unzip**: Remote AI tools often zip a parent directory instead of the root contents. Always inspect the extracted staging tree before overwriting.

* **Keep handoff files out of Git**: Exclude `GEMINI_HANDOFF.md` and `CHANGE_REPORT.md` from commits so the repository stays clean.

* **Do not bounce minor compile errors**: Fixing a missing import locally takes seconds and saves an entire manual ZIP relay round.

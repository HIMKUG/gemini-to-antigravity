<div align="center">

<img src="assets/banner.svg" alt="Gemini to Antigravity" width="100%"/>

# Gemini to Antigravity

**A deterministic two-AI relay: unlimited remote quota, local build authority.**

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg?style=for-the-badge)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-8b5cf6.svg?style=for-the-badge)](SKILL.md)
[![Agent Skills](https://img.shields.io/badge/Agent-Skills-4285F4.svg?style=for-the-badge)](https://docs.claude.com/en/docs/claude-code/skills)
[![No Telemetry](https://img.shields.io/badge/telemetry-none-0ea5e9.svg?style=for-the-badge)](#privacy--security)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-ec4899.svg?style=for-the-badge)](CONTRIBUTING.md)

[English](README.md) · [简体中文](README.zh-CN.md) · [Quick Start](#quick-start-in-60-seconds) · [Skill Spec](SKILL.md)

</div>

---

## Why this exists

Every serious coding agent hits the same wall: the model with the *best* reasoning has a metered quota, and the model with the *unlimited* quota cannot compile anything. You end up shuttling diffs by hand, losing context, and discovering at the very end that nothing builds.

**Gemini to Antigravity** formalizes that shuttle into a protocol.

The local agent — **A AI** (*Antigravity*: it holds the repository, the compiler, and the release gate) — owns diagnosis, review, and the build. The remote agent — **B AI** (*Gemini*: effectively unlimited compute budget, zero local toolchain) — owns bulk code mutation. The two are joined by exactly two artifacts:

```
one handoff ZIP   ─────────────────────────▶   B AI
one result ZIP    ◀─────────────────────────   B AI
```

Everything else — invariants, prompts, return contracts, error triage — is encoded so neither side can drift.

> The name is the contract. *Gemini* is the engine you borrow. *Antigravity* is the ground you never leave: your repo, your `git diff`, your build output, your signature on the release.

---

## The problem it solves

| Pain | Without this skill | With this skill |
| --- | --- | --- |
| **Quota exhaustion** | Burn your frontier-model quota on 400-line refactors | Push bulk work to an unlimited-quota model |
| **No toolchain remotely** | Remote model writes plausible code that never compiles | Local side always compiles, typechecks, and packages |
| **Blind trust** | You accept a remote "it's done" message | `git diff` is the source of truth, not the report |
| **Context loss** | Remote model forgot the architecture halfway through | `GEMINI_HANDOFF.md` is self-contained by design |
| **Relay ping-pong** | Three round trips to fix one missing import | Mechanical fixes are patched locally in seconds |
| **Archive hygiene** | `node_modules/` bloats the ZIP to 300 MB | Excluded by a named, auditable denylist |
| **Wrapper folders** | Files land one directory too deep and silently overwrite nothing | Staging extraction normalizes the root first |
| **Unclean history** | `GEMINI_HANDOFF.md` ends up committed | Handoff artifacts are explicitly untracked |

---

## How it works

<div align="center">
<img src="assets/flow.svg" alt="Relay loop" width="100%"/>
</div>

```
┌──────────────────────────── Phase 1 · Outbound ────────────────────────────┐
│                                                                            │
│   ①  Pre-diagnosis        Read source, logs, traces                         │
│                           Split Confirmed Issues  vs  Suspect Areas         │
│                                     │                                      │
│   ②  Handoff prompt       GEMINI_HANDOFF.md at ZIP root                     │
│                           → mission, constraints, return contract           │
│                                     │                                      │
│   ③  Package              ZIP_DEFLATED, compresslevel = 9                   │
│                           exclude .git, node_modules, build, dist, ...      │
│                                     │                                      │
└─────────────────────────────────────┼──────────────────────────────────────┘
                                      ▼
                              ┌───────────────┐
                              │   B AI / ZIP  │   heavy mutation, no build
                              └───────┬───────┘
                                      ▼
┌──────────────────────────── Phase 2 · Inbound ─────────────────────────────┐
│                                                                            │
│   ④  Safety checkpoint    git status → commit / named stash                 │
│                                     │                                      │
│   ⑤  Staged extraction    inspect layout → normalize wrapper folder          │
│                           read CHANGE_REPORT.md in full                     │
│                           overwrite sources, honor "Deleted Files"           │
│                                     │                                      │
│   ⑥  Diff review          git status · git diff --stat · git diff            │
│                           cross-check against report + original request     │
│                                     │                                      │
│   ⑦  Build gate           typecheck → compile → test → release artifact     │
│                                     │                                      │
│   ⑧  Triage               mechanical  → fix locally, rebuild                │
│                           structural  → reject, rework ZIP                  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick start in 60 seconds

### Install

```bash
# Personal skills (available in every project)
git clone https://github.com/HIMKUG/gemini-to-antigravity.git \
  ~/.claude/skills/gemini-to-antigravity
```

```powershell
# Windows (PowerShell)
git clone https://github.com/HIMKUG/gemini-to-antigravity.git "$env:USERPROFILE\.claude\skills\gemini-to-antigravity"
```

Or drop the folder into `.claude/skills/` inside a single project to scope it there.

Verify it loaded:

```bash
claude --debug 2>&1 | grep -i gemini-to-antigravity
```

### Use it — outbound

> "Package this repo for Gemini. The crash is in `src/core/scheduler.ts:112`. Hand off the fix and ask it to audit the retry path too."

What happens: pre-diagnosis → `GEMINI_HANDOFF.md` → `repo-handoff-<date>.zip` at maximum compression → exact path and byte size printed for you to upload.

### Use it — inbound

> "Here's the ZIP Gemini sent back. Apply it, review the diff, and build the release APK."

What happens: checkpoint → staged extract → overwrite → `git diff` review → build → local triage → release path reported.

---

## What makes it rigorous

### 1 · The handoff prompt is self-contained by contract

B AI has no memory of this skill, this repository, or your earlier conversation. Every invariant it must honor lives inside `GEMINI_HANDOFF.md`:

| Section | Guarantee |
| --- | --- |
| **Environment Notice** | Tells B AI it has no compiler, so it must reason about imports, types, and symbols statically |
| **User Original Request (Verbatim)** | No paraphrase drift — the requirement survives transport byte-for-byte |
| **Confirmed Issues** | File path + line range + root cause, verified locally before handoff |
| **Suspect Areas** | Named blind spots B AI must audit, separating "known broken" from "possibly broken" |
| **Deliverable & Return Contract** | Exact ZIP shape, exact `CHANGE_REPORT.md` schema, explicit `Deleted Files` list |

### 2 · The archive is a specification, not a dump

| Included | Excluded (denylist) |
| --- | --- |
| Full source tree, all configs, lockfiles, assets | `.git/` |
| `GEMINI_HANDOFF.md` at root | `node_modules/`, `.venv/`, `__pycache__/` |
| `.gitignore`-relevant source files | `target/`, `build/`, `dist/`, `.gradle/`, `.dart_tool/` |
| Relative directory layout, byte-exact | `.idea/`, `.vs/`, `.DS_Store` |

Compression: `zipfile.ZIP_DEFLATED` at `compresslevel=9` (cross-platform, no external binary), or `zip -9 -r` where available. The ZIP is verified post-write: root-level `GEMINI_HANDOFF.md`, preserved relative layout.

### 3 · Integration is a two-key operation

You never extract a remote archive straight into your working tree. Two gates:

1. **Safety checkpoint** — `git status` first; commit or create a named stash so the pre-overwrite state is always recoverable.
2. **Staged extraction** — unpack into a temp directory, detect a wrapper folder (`project_name/`), normalize the source root, read the report *before* copying a single file.

### 4 · Git is the judge

The remote report is a *claim*. `git diff` is the *evidence*. Review is mandatory and structural:

- `git status` and `git diff --stat` for the blast radius
- full `git diff` for intent
- cross-check against `CHANGE_REPORT.md` **and** the original verbatim request
- explicit hunting for truncation, reformat noise, and out-of-scope edits

### 5 · Error triage is a decision, not a reflex

| Class | Examples | Action |
| --- | --- | --- |
| **Mechanical** | missing import, forgotten dependency, syntax typo, visibility mismatch | Fix locally, rebuild, ship |
| **Structural** | core requirement missed, architectural defect, diff review failed | Stop patching; write a rework handoff with logs + diff excerpts; resend |

A missing import costs seconds locally and a full human relay round remotely. The protocol forbids bouncing it.

---

## Repository layout

```
gemini-to-antigravity/
├── SKILL.md                      # The skill: agent-facing specification
├── README.md                     # This document
├── README.zh-CN.md               # 简体中文版
├── LICENSE                       # MIT
├── assets/
│   ├── banner.svg                # README header
│   └── flow.svg                  # Relay diagram
├── examples/
│   ├── GEMINI_HANDOFF.example.md # Filled-out outbound prompt
│   └── CHANGE_REPORT.example.md  # Filled-out inbound report
├── scripts/
│   └── pack_handoff.py           # Deterministic ZIP -9 packager
└── docs/
    └── PROTOCOL.md               # Formal invariants and message schema
```

---

## The return contract

B AI must answer with exactly one ZIP:

```text
<result>.zip
├── <source tree, unchanged relative layout>
└── CHANGE_REPORT.md
```

`CHANGE_REPORT.md` schema:

```markdown
## Summary of Changes
- path/to/file.ext — <what changed and why>

## Findings on Suspect Areas
- path/module — <what was checked, what was found, what was fixed>

## Deleted Files
- path/to/removed.ext        # or the literal word: None

## Build & Dependency Notes
- new packages, permissions, imports, or build steps to verify locally
```

A report missing any of these four sections is treated as an incomplete deliverable.

---

## Compatibility

| Surface | Support |
| --- | --- |
| Claude Code (CLI / desktop / IDE) | ✅ Skills auto-discovered from `~/.claude/skills` |
| Any agent runtime reading `SKILL.md` | ✅ Plain-markdown YAML frontmatter |
| Repository languages | ✅ Language-agnostic — TypeScript, Python, Rust, Kotlin, Dart, C++, anything |
| Release targets | ✅ Binaries, installers, APKs, bundles, containers |
| OS | ✅ Windows, macOS, Linux |
| Network | ❌ None required — the relay is file-based by design |

---

## Design principles

1. **Local authority is non-negotiable.** The side with the compiler always has the final word.
2. **Artifacts over promises.** A ZIP and a diff outrank any prose claim of completion.
3. **Every rule travels with the payload.** Self-contained prompts beat implicit context.
4. **Cheap fixes stay cheap.** Mechanical errors never justify a relay round.
5. **Smallest clean archive.** Excluded bytes are excluded risk.
6. **Reversible by default.** Safety checkpoint before every overwrite.
7. **No hidden state.** The whole protocol is readable markdown in this repo.

---

## Privacy & security

- **No telemetry.** The skill makes no network calls and reports nothing anywhere.
- **No credentials.** Handoff artifacts contain source code only — never `.env`, tokens, or keys. Add your own secret patterns to the denylist when packing sensitive repos.
- **Human-in-the-loop transfer.** You move the ZIP yourself; nothing is uploaded automatically.
- **Untracked handoff files.** `GEMINI_HANDOFF.md` and `CHANGE_REPORT.md` are kept out of commits so repository history stays clean.

---

## FAQ

**Why not just use one model with a bigger quota?**
Because quota and toolchain rarely co-locate. This protocol lets you compose the best of both without losing the release gate.

**Can A AI be any local agent?**
Yes. Anything that can read/write files, run `git`, and execute a build qualifies. `SKILL.md` is model-agnostic.

**Can B AI be something other than Gemini?**
Yes — any remote model that accepts a ZIP and returns a ZIP. The contract is the interface.

**How large can a handoff get?**
Bounded by source size after exclusions, typically a few megabytes. Binary assets are the practical limit; consider a manifest for very large media.

**What if B AI returns a wrapper folder?**
Expected. Staged extraction normalizes it. This is the single most common remote-ZIP failure mode and it is explicitly handled.

**What if B AI deletes a file I need?**
The `Deleted Files` section is the only authorized deletion channel. Anything deleted without appearing there is a protocol violation surfaced during diff review.

**Does this work for monorepos?**
Yes. The exclusion list is path-relative and the layout is preserved verbatim, so workspace structure survives intact.

**Is there an automated packager?**
Yes — [`scripts/pack_handoff.py`](scripts/pack_handoff.py) produces a deterministic `-9` archive with the default denylist.

---

## Roadmap

- [ ] `--verify` audit mode for returned ZIPs (layout, report schema, deletions)
- [ ] Configurable denylist profiles (`web`, `android`, `python`, `monorepo`)
- [ ] Handoff diff preview: summarize what changed before overwriting
- [ ] Multi-round relay history with per-round checkpoints
- [ ] Pre-flight lint for `GEMINI_HANDOFF.md` completeness

See [open issues](https://github.com/HIMKUG/gemini-to-antigravity/issues) — proposals welcome.

---

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md), then open a PR. Keep `SKILL.md` model-agnostic, keep the protocol readable, and keep the diff small.

```bash
git clone https://github.com/HIMKUG/gemini-to-antigravity.git
cd gemini-to-antigravity
# edit SKILL.md / docs, then:
git checkout -b feat/your-change
```

---

## License

MIT © 2026 HIMKUG — see [LICENSE](LICENSE).

<div align="center">

**Borrow the engine. Keep the ground.**

<sub>Built for agents that ship, not agents that chat.</sub>

</div>

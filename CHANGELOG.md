# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-11-24

### Changed — the handoff is now a ledger

- **Precision rule.** Every `F-nn` heading carries the most specific locator available: a line range, a single line, or a bare file path. A finding with no locator is downgraded to `S-nn`, never filed as a fault.
- **No remedies.** `F-nn` states what the code does, what it must do, what triggers the failure, and what breaks. It states no patch, no target API, and no sketch of the fix — so review checks whether the fault is gone, not whether B AI followed A AI's guess.
- **Requirements restated.** §3 turns each sentence of the verbatim request into a `U-nn` with an observable acceptance test.
- **Execution ledger.** B AI appends one entry per ID to §6 *as it finishes each one*, then completes the §7 self-audit table with line-level evidence. A failed entry is acceptable when it names a blocker and a stopping point; an absent entry is not.
- **Same file back.** B AI returns the handoff it received, with §6 and §7 filled. There is no separate `CHANGE_REPORT.md` — a separate report is a summary, and summaries are where claimed-but-unfinished work hides.
- **Rework appends a death record.** A failed round adds §9 rather than rewriting the prompt: the failed claims, verbatim build evidence, drift, and the scope for the next round. B AI must keep appending to the same document, one ID at a time.

### Added

- `scripts/check_ledger.py` — dependency-free completeness gate. Extracts every ID from §2–§4, asserts one §6 entry and one §7 row each, rejects duplicate IDs, rejects a `DONE` without files and lines, rejects a `FAILED` without blocker and stopping point, and rejects a §6/§7 status mismatch. Exit 1 on any violation.
- `examples/GEMINI_HANDOFF.lazy-round.md` — a deliberately bad return (missing entries, prose substituting for items, unverifiable `DONE`s) used to calibrate the checker and the review.
- CI: locator gate on every fault heading, a remedy-language scan on `Problem` fields, and both checker outcomes asserted (example passes, lazy round fails).

### Removed

- `examples/CHANGE_REPORT.example.md` and the four-section report schema. Superseded by the in-file ledger.

## [1.0.0] — 2026-11-24

### Added
- `SKILL.md` — two-phase relay protocol (outbound handoff, inbound integration), with error triage rules and gotchas.
- `README.md` / `README.zh-CN.md` — overview, quick start, recipes, cost model, threat model.
- `docs/PROTOCOL.md` — formal role table, artifact schemas, state machine, invariants, failure catalogue, conformance checklist.
- `examples/GEMINI_HANDOFF.example.md` — a filled-out outbound prompt with confirmed issues and suspect areas.
- `examples/CHANGE_REPORT.example.md` — a filled-out inbound report covering all four required sections.
- `scripts/pack_handoff.py` — dependency-free ZIP packager at DEFLATE level 9 with a denylist, a secret scan, and post-write verification.
- `assets/banner.svg`, `assets/flow.svg` — header and relay diagram.
- `.github/workflows/validate.yml` — CI checking frontmatter, example schemas, packager behavior, and relative links.

### Fixed
- Original `SKILL.md` frontmatter used `## name:` / `## description:` headings instead of YAML key-value pairs, which skill loaders do not parse. Converted to a standard YAML block with `name`, `description`, and `license`.
- The packager would have written `GEMINI_HANDOFF.md` twice when it already lived inside the repository; the source walk now skips the handoff path.

# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

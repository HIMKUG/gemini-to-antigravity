# Comparison: relay protocols and adjacent approaches

Where Gemini to Antigravity sits relative to the other ways people move work
between AI agents. The comparisons are about *protocol shape*, not vendors.

## The field

| Approach | What it optimizes | What it sacrifices |
| --- | --- | --- |
| **Chat copy-paste** (paste files into a chat window) | Zero setup | Lossy transport, no layout, no record of intent, re-explains context every round |
| **Single agent with subagents** | Latency — everything runs in one runtime | Subagents share the same quota and the same toolchain; no quota arbitrage |
| **Git branch handoff** (push a branch, remote agent pulls) | Clean history, native review | Requires the remote agent to have repo access and network; not usable with a chat-only model |
| **Patch/diff relay** (send a `.patch`, receive a `.patch`) | Minimal bytes | Fragile on renames, binary files, and multi-file layout changes; no snapshot to reason against |
| **Full-repo archive relay** (this protocol) | Complete context, deterministic layout, quota arbitrage | Larger transfer, requiring a deliberate exclusion list |
| **MCP tool sharing** (remote agent calls your local tools) | Live access, no transfer | Requires the remote side to reach your machine; a security and availability coupling |

## Why the archive wins for this specific asymmetry

The asymmetry is precise: **the cheap model has no toolchain, the toolchain
holder has no cheap quota.** Every approach above either assumes both sides can
run tools (subagents, MCP, branch handoff) or drops structural information
(copy-paste, patch relay). A full-source archive is the smallest artifact that
preserves *everything the remote side needs to reason correctly*:

- relative layout, so imports resolve
- configs and lockfiles, so dependency questions are answerable
- tests, so the remote model can read the intended contract
- the verbatim request, so intent survives transport

`-9` compression keeps the cost of that completeness near the cost of a patch
for typical source trees.

## Failure modes by approach

| Failure | Copy-paste | Patch relay | Branch handoff | Archive relay |
| --- | --- | --- | --- | --- |
| Rename/restructure | ✗ common | ✗ common | ✔ | ✔ |
| Import graph questions | ✗ context missing | ~ partial | ✔ | ✔ |
| Quota arbitrage | ✔ | ✔ | ✔ | ✔ |
| Works without repo access remotely | ✔ | ✔ | ✗ | ✔ |
| Wrapper-folder risk | — | — | — | ✗ handled by staging |
| Secret leakage risk | ✗ manual | ✗ manual | ✔ (gitignore) | ~ handled by denylist |
| Auditable record | ✗ | ~ patch file | ✔ commit | ✔ archive + report |
| Works with a chat-only model | ✔ | ✔ | ✗ | ✔ |

## When to use something else

- **Remote agent has live repo access and you trust it**: a branch handoff gives
  you better history and native review than any archive.
- **The change is a single file**: a patch is smaller and faster; the archive's
  completeness buys you nothing.
- **Both sides can run tools and share a quota**: subagents are simpler, and
  this protocol's relay ceremony is overhead.
- **You need real-time collaboration, not batched delegation**: MCP tool sharing
  beats a file relay.

The protocol is for *batched, heavy, quota-arbitraged delegation with a local
release gate*. Choose it when that sentence describes your situation.

# Installing this skill into an agent runtime

`SKILL.md` is a plain-markdown file with YAML frontmatter. Any runtime that can
read a directory of skills, or that lets you attach a system prompt, can run it.
This page covers the common cases.

## Claude Code

Skills are discovered from two places:

| Scope | Path | Availability |
| --- | --- | --- |
| Personal | `~/.claude/skills/gemini-to-antigravity/` | Every project |
| Project | `<repo>/.claude/skills/gemini-to-antigravity/` | That repository only |
| Plugin | `<plugin>/skills/gemini-to-antigravity/` | Wherever the plugin is enabled |

```bash
# Personal
git clone https://github.com/HIMKUG/gemini-to-antigravity.git \
  ~/.claude/skills/gemini-to-antigravity
```

```powershell
# Windows
git clone https://github.com/HIMKUG/gemini-to-antigravity.git "$env:USERPROFILE\.claude\skills\gemini-to-antigravity"
```

The directory name and the frontmatter `name` should match; Claude Code uses
the frontmatter value, and a mismatch makes the skill harder to find.

Verify:

```bash
claude --debug
# look for: gemini-to-antigravity  →  loaded
```

Then either let the model choose it, or name it explicitly:

```text
/gemini-to-antigravity package this repo for Gemini and hand off the fix
```

## Cursor / Windsurf / VS Code agents

These runtimes do not have a skill discovery directory, so use one of two
approaches:

1. **Rules file** — copy the body of `SKILL.md` (everything after the frontmatter)
   into `.cursor/rules/gemini-to-antigravity.mdc`, or the equivalent rules
   location, with a description that mentions ZIP handoff and two-agent relay.
2. **Prompt attachment** — attach `SKILL.md` to the conversation when you need
   the workflow, then ask for the specific phase.

Either way, the operative content is the same: the phases, the handoff schema,
and the triage rule.

## Codex / Gemini CLI / other terminal agents

Point the agent at the repository and ask it to follow `SKILL.md`:

```text
Read SKILL.md and follow it for this task: <your request>
```

If the runtime supports an instruction file, add a single line to `AGENTS.md`
or the equivalent:

```markdown
For cross-agent ZIP handoffs, follow https://github.com/HIMKUG/gemini-to-antigravity/blob/main/SKILL.md
```

## Remote model (B AI)

B AI needs **nothing installed**. It receives `GEMINI_HANDOFF.md` inside the ZIP
and reads that file. This is the central design choice: the protocol is
transported with the payload, not assumed to be installed at the destination.

If you are sending a handoff to a model that can only accept a text prompt (no
file upload), paste the contents of `GEMINI_HANDOFF.md` and attach the source as
a separate archive — the contract does not depend on the transport.

## Any MCP-capable runtime

If your runtime loads tools through MCP and you want the packager callable as a
tool, wrap `scripts/pack_handoff.py` in an MCP server exposing one tool:

```text
pack_handoff(repo_path: str, output_zip: str, handoff_path: str | None) -> {path, bytes, files}
```

The script already returns exactly those three fields on success and uses exit
codes 0/1/2, so a thin wrapper is sufficient. The script is dependency-free, so
no environment setup is needed beyond a Python 3.9+ interpreter.

## Checklist for a new runtime

- [ ] The runtime can read a directory of markdown skills, or you can paste `SKILL.md` into a prompt
- [ ] The agent can run shell commands (`git`, a ZIP utility, optionally Python)
- [ ] The agent can write files into the repository working tree
- [ ] You have a way to move a ZIP file to the remote model by hand
- [ ] You have a local build command you trust as the release gate

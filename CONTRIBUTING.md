# Contributing

Thanks for improving Gemini to Antigravity. This is a protocol repo: most changes are documentation and specification, and they are held to the same rigor as code.

## Ground rules

1. **Keep `SKILL.md` model-agnostic.** No vendor names in the procedural body; vendor examples belong in `examples/` or this file.
2. **Keep the protocol readable.** A new invariant must be stated in `docs/PROTOCOL.md`, not buried in prose.
3. **Keep diffs small.** One concern per pull request. No reformatting unrelated sections.
4. **Evidence over claims.** A change to protocol behavior needs a matching example or checklist item.

## Local checks

```bash
# 1. Frontmatter sanity: name + description present, description under 1024 chars
head -n 8 SKILL.md

# 2. Example schema shape: the report has the four required sections
grep -c '^## ' examples/CHANGE_REPORT.example.md

# 3. Packager smoke test on a scratch directory (needs a GEMINI_HANDOFF.md at root)
mkdir -p /tmp/smoke && printf 'smoke\n' > /tmp/smoke/app.txt
cp examples/GEMINI_HANDOFF.example.md /tmp/smoke/GEMINI_HANDOFF.md
python3 scripts/pack_handoff.py /tmp/smoke /tmp/smoke.zip
```

`pack_handoff.py` is dependency-free and runs on Python 3.9+; CI runs the same
checks in `.github/workflows/validate.yml`.

## Pull request checklist

- [ ] `SKILL.md` frontmatter intact and accurate
- [ ] `README.md` and `README.zh-CN.md` describe the same behavior
- [ ] Examples still match the schema in `docs/PROTOCOL.md`
- [ ] No secrets, credentials, or machine-specific paths added
- [ ] Commit message describes the *why*

## Reporting issues

Include: the two agents involved, the archive size, whether a wrapper folder appeared, and the relevant `git diff --stat`. Never paste repository content containing credentials.

## License

Contributions are accepted under the MIT License.

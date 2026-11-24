# Operations runbook

Day-to-day guidance for running relay rounds: sizing, scheduling, data hygiene,
and what to do when a round goes wrong.

## Round sizing

The archive is the unit of work, so size it deliberately.

| Repo size (post-exclusion) | Recommendation |
| --- | --- |
| < 1 MB | One handoff per feature; no splitting |
| 1–20 MB | One handoff per concern; check that binary assets are excluded |
| 20–100 MB | Split by package or module; keep the handoff prompt explicit about sub-roots |
| > 100 MB | Almost always an exclusion bug — check `node_modules`, build outputs, media |

Splitting rule: a handoff should fit in one remote response. If the change set
spans modules that the remote model would need to re-reason across, it is one
concern; if they are independent, split.

## Scheduling a relay

A relay round is idle while the remote model works. Plan around that:

1. **Batch outbound work.** Prepare two or three independent handoffs before
   sending, so the remote side is never idle waiting on you.
2. **Do reviewable local work while remote work runs.** Documentation, tests,
   or unrelated fixes that do not conflict with the handoff's file set.
3. **Never start a second handoff touching the same files.** It invalidates the
   first round's diff review.
4. **Checkpoint before every inbound merge.** If you made local commits while
   remote work was in flight, the checkpoint makes the diff review clean.

## Data hygiene

- Keep handoff ZIPs in one directory you can audit, named by round.
- A round name should identify the request, not the model: `handoff-auth-retry`
  beats `gemini-round-3`.
- Delete staging directories after each merge; they are the highest-risk place
  for stale files.
- Never commit the returned `GEMINI_HANDOFF.md`; the `.gitignore` in this repo
  already excludes it.

Suggested exclude additions for unusual repos:

```text
*.log            # analysis logs are often large and rarely needed
*.sqlite         # local databases
testdata/        # large fixtures — include only if the task needs them
vendor/          # only if the task touches dependencies
```

## Handling a failed round

| Symptom | First action | Then |
| --- | --- | --- |
| `check_ledger.py` reports missing IDs | Do not merge; do not read the diff yet | Append §9 naming the missing IDs; rework |
| §6 entries all arrive at the end, in identical format | Treat as a batched ledger — the work was likely not done in order | Review the diff harder than usual; require per-entry `Verified` |
| A `DONE` entry names lines the diff does not touch | The claim is false | Count it as a missing ID in §9 |
| An entry says "fixed" with no `Files`/`Lines` | Malformed entry | Reject; the checker flags it under `--strict` |
| Diff far larger than expected | Stop before building | §9 names the drifting files; narrowed rework |
| Build fails on a mechanical error | Patch locally | Continue; never bounce |
| Build fails structurally | §9 with verbatim compiler output | One rework round; a third failure means re-scope the task |
| A file vanished but no entry names it | Reject the round | Silent deletion is a protocol violation; §9 asks for the path |

## Escalation ladder

A round is allowed at most:

1. one outbound handoff
2. one rework round for structural defects
3. one final round for a narrowly-restated scope

After the third, stop relaying. Either split the task into smaller handoffs or
do the work locally. Escalating indefinitely means the scope was never clear.

A round that fails `check_ledger.py` does not consume a rework slot: it never
reached review, so it is resent rather than escalated. Track the difference —
a repeated ledger failure is a prompt problem, not a task problem.

## Review discipline

The ledger is a claim; the diff is evidence. In every round:

- Run `check_ledger.py` before reading anything else, so a lazy round fails in
  seconds instead of after a full diff read.
- Read the **full** diff, not `--stat`, at least once for files the remote model
  could plausibly get subtly wrong (concurrency, state machines, auth, parsers).
- Skim files the remote model only mechanically touched (renames, imports, docs).
- Re-read the `Verified` field of each `DONE` entry before the build, so an
  unexpected package does not surprise you in the lockfile diff.
- Confirm every deletion in §6 against `git status`.

## Calibrating against a lazy round

`examples/GEMINI_HANDOFF.lazy-round.md` is a deliberately bad return. Run the
checker against it once to see what the failure output looks like:

```bash
python scripts/check_ledger.py examples/GEMINI_HANDOFF.lazy-round.md
```

It exits non-zero and names the absent IDs and the malformed entries. Knowing
that output shape by memory makes round-one triage fast: you can quote the
checker's finding in §9 instead of paraphrasing it.

## Metrics worth tracking per round

Keep them somewhere cheap — one line per round is enough:

```
round=<name> ids=<n> done=<n> failed=<n> na=<n> diff_files=<n> diff_lines=<n> triage=<none|local|rework> build=<pass|fail> zip=<bytes>
```

Two contrasts are worth watching: a round whose `done` count matches `ids` but
whose `diff_files` is unusually small means entries claim work the diff does not
contain; a sudden rise in `zip` means exclusion drift. Neither is a code problem.

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
- Never commit `GEMINI_HANDOFF.md` or `CHANGE_REPORT.md`; the `.gitignore` in
  this repo already excludes them.

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
| Remote returns nothing usable | Confirm the ZIP was actually delivered and the handoff at root | Resend with a shorter, more explicit scope |
| Report missing a required section | Do not merge | Ask for a corrected report only — no code changes needed |
| Diff far larger than expected | Stop before building | Ask for a narrowed rework that restates the scope boundary |
| Build fails on a mechanical error | Patch locally | Continue; never bounce |
| Build fails structurally | Write a rework handoff with logs + diff excerpts | One rework round; a third failure means re-scope the task |
| Deletion reported as `None` but `git status` shows a removal | Reject the round | Ask for the exact paths — a silent deletion is a protocol violation |

## Escalation ladder

A round is allowed at most:

1. one outbound handoff
2. one rework round for structural defects
3. one final round for a narrowly-restated scope

After the third, stop relaying. Either split the task into smaller handoffs or
do the work locally. Escalating indefinitely means the scope was never clear.

## Review discipline

The report is a claim; the diff is evidence. In every round:

- Read the **full** diff, not `--stat`, at least once for files the remote model
  could plausibly get subtly wrong (concurrency, state machines, auth, parsers).
- Skim files the remote model only mechanically touched (renames, imports, docs).
- Re-read `Build & Dependency Notes` before the build, so an unexpected package
  does not surprise you in the lockfile diff.
- Confirm `Deleted Files` against `git status`.

## Metrics worth tracking per round

Keep them somewhere cheap — one line per round is enough:

```
round=<name> files_in=<n> diff_files=<n> diff_lines=<n> triage=<none|local|rework> build=<pass|fail> zip=<bytes>
```

Two rounds are worth comparing: a sudden rise in `diff_files` means scope drift;
a sudden rise in `zip` means exclusion drift. Neither is a code problem.

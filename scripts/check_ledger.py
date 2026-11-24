#!/usr/bin/env python3
"""Verify that a returned handoff ledger is complete before review begins.

Usage:
    python check_ledger.py <returned/GEMINI_HANDOFF.md> [--strict]

The returned handoff must carry, for every ID declared in §2 (F faults),
§3 (U requirements) and §4 (S suspects):
  - exactly one entry in §6 with STATUS: DONE | FAILED | NOT-APPLICABLE
  - exactly one row in §7 carrying the same status
and every DONE must prove itself with a file and a line reference, while every
FAILED must state its blocker and the point where work stopped.

Exit codes:
    0  ledger complete and internally consistent
    1  missing or duplicated IDs, or a malformed entry
    2  unusable input (missing file or missing required section)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VALID_STATUS = {"DONE", "FAILED", "NOT-APPLICABLE"}

SECTION_RE = re.compile(r"^##\s*([0-9]+)\.", re.MULTILINE)
ENTRY_RE = re.compile(r"^###\s+((?:F|U|S|X)-\d{2})\s*$", re.MULTILINE)
ROW_RE = re.compile(r"^\|\s*((?:F|U|S|X)-\d{2})\s*\|([^|]*)\|([^|]*)\|", re.MULTILINE)


def split_sections(text: str) -> dict[int, str]:
    """Map `## N.` section number to its body text."""
    starts = [(m.start(), int(m.group(1))) for m in SECTION_RE.finditer(text)]
    sections: dict[int, str] = {}
    for idx, (pos, num) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(text)
        sections[num] = text[pos:end]
    return sections


def declared_ids(section: str) -> list[str]:
    """IDs declared by `### ID · locator` headings inside §2, §3 or §4."""
    return re.findall(r"^###\s+((?:F|U|S|X)-\d{2})", section, re.MULTILINE)


def status_of(block: str) -> str | None:
    m = re.search(r"\*\*STATUS:\*\*[ \t]*([A-Za-z-]+)", block)
    if not m:
        m = re.search(r"STATUS[:\s]*([A-Za-z-]+)", block, re.IGNORECASE)
    return m.group(1).upper() if m else None


def has_field(block: str, name: str) -> bool:
    return bool(re.search(rf"\*\*{name}:\*\*[ \t]*(.+)$", block, re.MULTILINE))


def field_value(block: str, name: str) -> str:
    m = re.search(rf"\*\*{name}:\*\*[ \t]*(.+)$", block, re.MULTILINE)
    return m.group(1).strip() if m else ""


def entries(section: str) -> list[dict]:
    """Parse §6 into one record per heading."""
    heads = [(m.start(), m.group(1)) for m in ENTRY_RE.finditer(section)]
    out: list[dict] = []
    for idx, (pos, ident) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(section)
        block = section[pos:end]
        out.append(
            {
                "id": ident,
                "status": status_of(block),
                "files": field_value(block, "Files"),
                "lines": field_value(block, "Lines"),
                "blocker": field_value(block, "Blocker"),
                "stopped": field_value(block, "Stopped at"),
                "verified": field_value(block, "Verified"),
                "raw": block,
            }
        )
    return out


def audit_rows(section: str) -> list[tuple[str, str, str]]:
    """Parse §7's table into (id, status, evidence)."""
    rows: list[tuple[str, str, str]] = []
    for m in ROW_RE.finditer(section):
        ident, status, evidence = m.group(1), m.group(2).strip().upper(), m.group(3).strip()
        if status in VALID_STATUS:
            rows.append((ident, status, evidence))
    return rows


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff", type=Path, help="returned GEMINI_HANDOFF.md")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="also require every DONE entry to carry a non-empty Verified field",
    )
    args = parser.parse_args(argv)

    path = args.handoff
    if not path.is_file():
        print(f"[!] not a file: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    sections = split_sections(text)

    missing_sections = [n for n in (2, 3, 4, 6, 7) if n not in sections]
    if missing_sections:
        print(f"[!] missing section(s): {missing_sections}", file=sys.stderr)
        return 2

    declared_all = declared_ids(sections[2]) + declared_ids(sections[3]) + declared_ids(sections[4])
    declared: list[str] = []
    problems: list[str] = []

    for ident in declared_all:
        if ident not in declared:
            declared.append(ident)
    dup_declared = sorted({i for i in declared_all if declared_all.count(i) > 1})
    if dup_declared:
        problems.append(f"declared more than once in §2-§4: {dup_declared}")

    parsed = entries(sections[6])
    entry_ids = [e["id"] for e in parsed]
    dup_entries = sorted({i for i in entry_ids if entry_ids.count(i) > 1})
    if dup_entries:
        problems.append(f"duplicate §6 entries: {dup_entries}")

    missing_entries = [i for i in declared if i not in entry_ids]
    if missing_entries:
        problems.append(f"no §6 entry for: {missing_entries} (not attempted or silently skipped)")

    undeclared = sorted({i for i in entry_ids if i not in declared and not i.startswith("X-")})
    if undeclared:
        problems.append(f"§6 entry for an undeclared ID: {undeclared}")

    for e in parsed:
        if e["status"] not in VALID_STATUS:
            problems.append(f"{e['id']}: §6 entry has no valid STATUS (got {e['status']!r})")
        elif e["status"] == "DONE":
            if not e["files"] or e["files"] in {"-", "—", "none", "None"}:
                problems.append(f"{e['id']}: DONE without a Files field")
            if not e["lines"] or e["lines"] in {"-", "—", "none", "None"}:
                problems.append(f"{e['id']}: DONE without a Lines field")
            if args.strict and not e["verified"]:
                problems.append(f"{e['id']}: DONE without a Verified field")
        elif e["status"] == "FAILED":
            if not e["blocker"]:
                problems.append(f"{e['id']}: FAILED without a Blocker field")
            if not e["stopped"]:
                problems.append(f"{e['id']}: FAILED without a Stopped-at field")

    rows = audit_rows(sections[7])
    row_ids = [r[0] for r in rows]
    dup_rows = sorted({i for i in row_ids if row_ids.count(i) > 1})
    if dup_rows:
        problems.append(f"duplicate §7 rows: {dup_rows}")

    missing_rows = [i for i in declared if i not in row_ids]
    if missing_rows:
        problems.append(f"no §7 audit row for: {missing_rows}")

    entry_status = {e["id"]: e["status"] for e in parsed}
    for ident, status, evidence in rows:
        expected = entry_status.get(ident)
        if expected and status != expected:
            problems.append(f"{ident}: §6 says {expected}, §7 says {status}")
        if args.strict and status == "DONE" and not evidence:
            problems.append(f"{ident}: §7 DONE row has no evidence cell")

    if problems:
        print(f"LEDGER INCOMPLETE — {path}", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    done = sum(1 for e in parsed if e["status"] == "DONE")
    failed = sum(1 for e in parsed if e["status"] == "FAILED")
    na = sum(1 for e in parsed if e["status"] == "NOT-APPLICABLE")
    print(f"ledger ok — {len(declared)} declared, {done} done, {failed} failed, {na} not-applicable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Pack a repository into a maximum-compression handoff ZIP for a remote AI.

Usage:
    python pack_handoff.py <repo-dir> <output.zip> [--handoff GEMINI_HANDOFF.md]

The archive is written with DEFLATE level 9 and a named denylist so the result
stays small and free of build artifacts. `GEMINI_HANDOFF.md` is placed at the
archive root and verified after writing, and the archive is scanned for
secret-bearing filenames before the path is reported.

Exit codes:
    0  archive written and verified
    1  usage or IO error
    2  verification failed (handoff file missing from root)
"""

from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path

# Directories never included in a handoff. Path components are matched exactly.
EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        ".svn",
        ".hg",
        "node_modules",
        "target",
        "build",
        "dist",
        ".gradle",
        ".dart_tool",
        "__pycache__",
        ".venv",
        "venv",
        ".idea",
        ".vs",
        ".mypy_cache",
        ".pytest_cache",
        ".next",
        ".nuxt",
        ".turbo",
        "coverage",
    }
)

EXCLUDED_NAMES: frozenset[str] = frozenset({".DS_Store", "Thumbs.db"})

# Secret-bearing files that must never leave the machine.
SECRET_NAMES: frozenset[str] = frozenset(
    {
        ".env",
        ".env.local",
        ".env.production",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
    }
)


def is_excluded(rel: Path) -> bool:
    """True when a path relative to the repo root must not be archived."""
    if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
        return True
    name = rel.name
    if name in EXCLUDED_NAMES or name in SECRET_NAMES:
        return True
    if name.startswith(".env.") or name.endswith(".pem") or name.endswith(".key"):
        return True
    return False


def iter_source(root: Path, skip: Path | None = None) -> list[Path]:
    """Collect every file under root that survives the denylist.

    `skip` is excluded from the result so the handoff file is not written twice
    when it already lives inside the repository.
    """
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        base = Path(dirpath)
        for filename in filenames:
            full = base / filename
            if skip is not None and full == skip:
                continue
            try:
                rel = full.relative_to(root)
            except ValueError:
                continue
            if is_excluded(rel):
                continue
            if full.is_symlink():
                continue
            files.append(full)
    return files


def write_archive(root: Path, out: Path, handoff: Path | None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    skip = handoff if handoff and handoff.is_file() else None
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        if skip:
            zf.write(skip, arcname=skip.name)
        for full in iter_source(root, skip=skip):
            zf.write(full, arcname=str(full.relative_to(root)).replace(os.sep, "/"))


def verify_archive(out: Path, handoff_name: str | None) -> bool:
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
        if handoff_name and handoff_name not in names:
            print(f"[!] {handoff_name} missing from archive root", file=sys.stderr)
            return False
        if not names:
            print("[!] archive is empty", file=sys.stderr)
            return False
        leaked = [n for n in names if Path(n).name in SECRET_NAMES]
        if leaked:
            print(f"[!] secret-bearing files in archive: {leaked}", file=sys.stderr)
            return False
    return True


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path, help="repository directory to pack")
    parser.add_argument("output", type=Path, help="output ZIP path")
    parser.add_argument(
        "--handoff",
        type=Path,
        default=None,
        help="handoff markdown file; defaults to <repo>/GEMINI_HANDOFF.md if present",
    )
    args = parser.parse_args(argv)

    root = args.repo.resolve()
    if not root.is_dir():
        print(f"[!] not a directory: {root}", file=sys.stderr)
        return 1

    handoff = args.handoff.resolve() if args.handoff else root / "GEMINI_HANDOFF.md"
    if not handoff.is_file():
        print(f"[!] handoff file not found: {handoff}", file=sys.stderr)
        return 1

    out = args.output.resolve()
    write_archive(root, out, handoff)

    if not verify_archive(out, handoff.name):
        return 2

    size = out.stat().st_size
    count = len(iter_source(root, skip=handoff))
    print(f"handoff  {out}")
    print(f"files    {count}")
    print(f"bytes    {size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

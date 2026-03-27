#!/usr/bin/env python3
"""
audio_automation_utils.py
Small CLI utility for audio workflow file operations.

Commands:
  inventory   Scan a folder and export a CSV file listing.
  rename      Batch rename files with prefix, suffix, or sequential numbering.
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def cmd_inventory(args):
    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else folder / "inventory.csv"
    pattern = f"**/*" if args.recursive else "*"

    rows = []
    for p in sorted(folder.glob(pattern)):
        if not p.is_file():
            continue
        stat = p.stat()
        rows.append({
            "name": p.name,
            "extension": p.suffix.lower(),
            "size_bytes": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "relative_path": str(p.relative_to(folder)),
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "extension", "size_bytes", "size_kb", "modified", "relative_path"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Inventory: {len(rows)} files → {output_path}")


# ---------------------------------------------------------------------------
# Rename
# ---------------------------------------------------------------------------

def build_new_name(original: Path, prefix: str, suffix: str, index: int, use_number: bool) -> str:
    stem = original.stem
    ext = original.suffix
    if use_number:
        return f"{prefix}{index:04d}{suffix}{ext}"
    return f"{prefix}{stem}{suffix}{ext}"


def cmd_rename(args):
    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    ext_filter = args.ext.lower() if args.ext else None
    files = sorted(p for p in folder.iterdir() if p.is_file())

    if ext_filter:
        files = [p for p in files if p.suffix.lower() == ext_filter]

    if not files:
        print("No files matched.")
        return

    prefix = args.prefix or ""
    suffix = args.suffix or ""
    use_number = args.number
    dry_run = args.dry_run

    if dry_run:
        print("Dry run — no files will be changed.\n")

    changes = []
    for i, p in enumerate(files, start=1):
        new_name = build_new_name(p, prefix, suffix, i, use_number)
        new_path = p.parent / new_name
        changes.append((p, new_path))
        status = "→" if not dry_run else "(dry)"
        print(f"  {p.name}  {status}  {new_name}")

    if dry_run:
        print(f"\n{len(changes)} files would be renamed. Run without --dry-run to apply.")
        return

    conflicts = [new for _, new in changes if new.exists()]
    if conflicts:
        print(f"\nError: {len(conflicts)} target name(s) already exist. Aborting.", file=sys.stderr)
        sys.exit(1)

    for old, new in changes:
        old.rename(new)

    print(f"\n{len(changes)} files renamed.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog="audio_automation_utils",
        description="Audio workflow file utilities: inventory export and batch rename.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # inventory
    p_inv = sub.add_parser("inventory", help="Export folder contents to CSV.")
    p_inv.add_argument("folder", help="Path to scan.")
    p_inv.add_argument("--output", "-o", help="Output CSV path (default: <folder>/inventory.csv).")
    p_inv.add_argument("--recursive", "-r", action="store_true", help="Recurse into subdirectories.")

    # rename
    p_ren = sub.add_parser("rename", help="Batch rename files.")
    p_ren.add_argument("folder", help="Folder containing files to rename.")
    p_ren.add_argument("--prefix", help="String to prepend to each filename.")
    p_ren.add_argument("--suffix", help="String to append before the extension.")
    p_ren.add_argument("--ext", help="Filter by extension, e.g. .wav")
    p_ren.add_argument("--number", action="store_true", help="Replace stem with 4-digit sequential number.")
    p_ren.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files.")

    args = parser.parse_args()

    if args.command == "inventory":
        cmd_inventory(args)
    elif args.command == "rename":
        cmd_rename(args)


if __name__ == "__main__":
    main()

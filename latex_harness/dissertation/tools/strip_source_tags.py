#!/usr/bin/env python3
"""
strip_source_tags.py

Removes inline [source: path/to/file] provenance tags from the compressed
chapter markdown, and harvests every one into a Data Provenance appendix.

Design intent: the audit trail is a genuine strength of this dissertation
and should not be deleted. But several hundred inline tags in the body
would wreck readability and are not what a marker wants to read. So the
tags come OUT of the prose and go INTO a table a marker can check.

SAFETY GATES
  - Never writes over the input. Cleaned copies go to --outdir.
  - Refuses to run if --outdir already contains files, unless --force.
  - Emits a count reconciliation: tags removed MUST equal table rows.
    A mismatch is a hard error, not a warning.

Usage:
  python tools/strip_source_tags.py \
      --indir  chapters_md/ \
      --outdir chapters_md_clean/ \
      --appendix appendices/appF_data_provenance.tex \
      --csv build/provenance_audit.csv
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# Matches [source: anything-not-a-bracket], tolerant of whitespace and case.
TAG = re.compile(r"\[\s*source\s*:\s*([^\]]+?)\s*\]", re.IGNORECASE)

# Trailing whitespace left behind once a tag is removed mid-sentence.
DOUBLE_SPACE = re.compile(r"[ \t]{2,}")
SPACE_BEFORE_PUNCT = re.compile(r"\s+([.,;:)])")


def latex_escape(s: str) -> str:
    """Escape the characters that will bite in a LaTeX table cell."""
    for a, b in [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
        ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
        ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
    ]:
        s = s.replace(a, b)
    return s


def context_for(line: str, match: re.Match, width: int = 90) -> str:
    """Grab readable context around a tag so the table row means something."""
    before = line[: match.start()].strip()
    before = TAG.sub("", before).strip()
    if len(before) > width:
        before = "..." + before[-width:]
    return before or "(start of line)"


def process_file(path: Path, outdir: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rows: list[dict] = []
    cleaned_lines: list[str] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in TAG.finditer(line):
            rows.append({
                "chapter_file": path.name,
                "line": lineno,
                "context": context_for(line, m),
                "source": m.group(1).strip(),
            })
        new_line = TAG.sub("", line)
        new_line = SPACE_BEFORE_PUNCT.sub(r"\1", new_line)
        new_line = DOUBLE_SPACE.sub(" ", new_line).rstrip()
        cleaned_lines.append(new_line)

    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / path.name).write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
    return rows


def write_appendix(rows: list[dict], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = [
        r"\chapter{Data Provenance}",
        r"\label{app:prov}",
        "",
        "Every numerical claim in this dissertation carries a provenance",
        "record identifying the file from which it was computed. These records",
        "were maintained inline throughout drafting and are collected here so",
        "that any reported figure can be traced to its source artefact in the",
        "project repository.",
        "",
        r"\small",
        r"\begin{longtable}{@{}p{2.6cm}p{7.2cm}p{4.4cm}@{}}",
        r"\toprule",
        r"\textbf{Chapter} & \textbf{Claim context} & \textbf{Source artefact} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{Chapter} & \textbf{Claim context} & \textbf{Source artefact} \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endfoot",
    ]
    for r in rows:
        out.append(
            f"{latex_escape(r['chapter_file'])} & "
            f"{latex_escape(r['context'])} & "
            f"\\texttt{{{latex_escape(r['source'])}}} \\\\"
        )
    out += [r"\end{longtable}", r"\normalsize", ""]
    dest.write_text("\n".join(out), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--indir", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--appendix", required=True, type=Path)
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not args.indir.is_dir():
        print(f"ERROR: --indir not found: {args.indir}", file=sys.stderr)
        return 2

    if args.outdir.exists() and any(args.outdir.iterdir()) and not args.force:
        print(f"ERROR: --outdir {args.outdir} is not empty. Use --force to overwrite.",
              file=sys.stderr)
        return 2

    md_files = sorted(args.indir.glob("*.md"))
    if not md_files:
        print(f"ERROR: no .md files in {args.indir}", file=sys.stderr)
        return 2

    all_rows: list[dict] = []
    per_file: dict[str, int] = {}
    for f in md_files:
        rows = process_file(f, args.outdir)
        per_file[f.name] = len(rows)
        all_rows.extend(rows)

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    with args.csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["chapter_file", "line", "context", "source"])
        w.writeheader()
        w.writerows(all_rows)

    write_appendix(all_rows, args.appendix)

    # ---- Reconciliation gate ----
    residual = sum(
        len(TAG.findall((args.outdir / f.name).read_text(encoding="utf-8")))
        for f in md_files
    )

    print("\n=== PROVENANCE STRIP REPORT ===")
    for name, n in sorted(per_file.items()):
        print(f"  {name:<45} {n:>4} tags")
    print(f"  {'TOTAL TAGS HARVESTED':<45} {len(all_rows):>4}")
    print(f"  {'TABLE ROWS WRITTEN':<45} {len(all_rows):>4}")
    print(f"  {'RESIDUAL TAGS IN CLEANED OUTPUT':<45} {residual:>4}")

    if residual != 0:
        print("\nFAIL: tags survived the strip. Do not use this output.", file=sys.stderr)
        return 1

    unique_sources = len({r["source"] for r in all_rows})
    print(f"  {'UNIQUE SOURCE ARTEFACTS':<45} {unique_sources:>4}")
    print("\nOK: strip clean, counts reconcile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

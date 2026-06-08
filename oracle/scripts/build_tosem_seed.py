#!/usr/bin/env python3
"""
We extract known bugs and create empty semantic-labeling columns for independent oracle construction.
This script parses the TOSEM SolidityStateStudy inconsistent-state-update
artifact and produces oracle/tosem_seed_raw.csv.
"""
from __future__ import annotations
import argparse, csv, re
from pathlib import Path

ROOT_CAUSE_DIR = "Inconsistent-State-Update-Vulnerabilities/Classification-by-Root-Causes"
RAW_COLUMNS = [
    "oracle_id",
    "source_dataset",
    "source_category",
    "source_subcategory",
    "serial_number",
    "reporting_time",
    "bug_link",
    "finding_slug",
    "contest_slug",
    "finding_id",
    "project_slug",
    "source_root_cause",
    "source_exploitation_method",
    "source_fix_strategy",
    "raw_line",
    "source_file",
]
LINK_RE = re.compile(r"\[([^\]]*#[hmql]-\d+[^\]]*)\]\(([^)]+)\)", re.I)
SLUG_RE = re.compile(r"(?P<contest>20\d{2}-(?:\d{2}|[a-z]{3})-[a-z0-9-]+)#(?P<fid>[hmql]-\d+)", re.I)
SERIAL_DATE_RE = re.compile(r"^\s*\|?\s*(?P<num>\d+)\s*\|?\s*(?P<date>20\d{2}-\d{2}-\d{2})", re.I)

def clean_cell(s: str) -> str:
    s = s.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip().strip("|").strip()

# Convert Code4rena contest slug to approximate project slug (e.g. 2021-12-vader -> vader)
def slug_to_project(contest_slug: str):
    s = contest_slug.lower()
    s = re.sub(r"^20\d{2}-\d{2}-", "", s)
    s = re.sub(r"^20\d{2}-[a-z]{3}-", "", s)
    s = re.sub(r"-\d+$", "", s)
    return s

# Parse an .md table row and return cells if this looks like a row containing a C4A finding
def parse_pipe_row(line):
    if not re.search(r"#[hmql]-\d+", line.lower()): return None
    if "|" not in line: return None

    cells = [clean_cell(c) for c in line.strip().split("|")]
    cells = [c for c in cells if c != ""]
    if len(cells) < 5: return None
    return cells

# Fallback for rendered/plain .md lines. Split-root cause/exploitation/fix should be manually checked later.
def fallback_parse_line(line: str):
    if not re.search(r"#[hmql]-\d+", line.lower()): return None

    m = LINK_RE.search(line)
    if not m: return None

    link_text, url = m.group(1), m.group(2)
    sm = SLUG_RE.search(link_text)
    if not sm: return None

    serial, reporting_time = "", ""
    dm = SERIAL_DATE_RE.search(line)
    if dm: serial, reporting_time = dm.group("num"), dm.group("date")

    # Remove prefix through finding link; remaining text is src prose
    rest = line[m.end():].strip()
    return {
        "serial_number": serial,
        "reporting_time": reporting_time,
        "bug_link": url,
        "finding_slug": sm.group(0).lower(),
        "contest_slug": sm.group("contest").lower(),
        "finding_id": sm.group("fid").lower(),
        "project_slug": slug_to_project(sm.group("contest")),
        "source_root_cause": clean_cell(rest),
        "source_exploitation_method": "",
        "source_fix_strategy": "",
    }

# Serial number | Reporting time | Bug link | Root cause | Exploitation method | Fix strategy
def parse_markdown_row(line):
    cells = parse_pipe_row(line)
    if cells:
        link_idx = None
        for i, c in enumerate(cells):
            if re.search(r"#[hmql]-\d+", c.lower()):
                link_idx = i
                break
        if link_idx is None: return None

        m = LINK_RE.search(cells[link_idx])
        # Raw GitHub rendering can sometimes strip markdown. Try direct slug
        if not m:
            direct = SLUG_RE.search(cells[link_idx])
            if not direct: return None
            url = ""
            finding_slug = direct.group(0).lower()
            contest_slug = direct.group("contest").lower()
            finding_id = direct.group("fid").lower()
        else:
            url = m.group(2)
            sm = SLUG_RE.search(m.group(1))
            if not sm: return None
            finding_slug = sm.group(0).lower()
            contest_slug = sm.group("contest").lower()
            finding_id = sm.group("fid").lower()

        serial_number = cells[0] if len(cells) > 0 else ""
        reporting_time = cells[1] if len(cells) > 1 else ""
        return {
            "serial_number": serial_number,
            "reporting_time": reporting_time,
            "bug_link": url,
            "finding_slug": finding_slug,
            "contest_slug": contest_slug,
            "finding_id": finding_id,
            "project_slug": slug_to_project(contest_slug),
            "source_root_cause": cells[link_idx + 1] if len(cells) > link_idx + 1 else "",
            "source_exploitation_method": cells[link_idx + 2] if len(cells) > link_idx + 2 else "",
            "source_fix_strategy": cells[link_idx + 3] if len(cells) > link_idx + 3 else "",
        }
    return fallback_parse_line(line)

# Parent folder is the category
def category_from_path(path): return path.parent.name.replace("_", "/").strip()

def current_subcategory(line, old):
    stripped = line.strip()
    if stripped.startswith("###"): return clean_cell(stripped.lstrip("#"))
    return old

def iter_root_cause_readmes(tosem_repo):
    root = tosem_repo / ROOT_CAUSE_DIR
    if not root.exists(): raise FileNotFoundError(f"TOSEM root-cause dir not found: {root}")
    yield from sorted(root.glob("*/README.md"))

def build_rows(tosem_repo):
    rows, counters = [], {}
    for md in iter_root_cause_readmes(tosem_repo):
        source_category = category_from_path(md)
        source_subcategory = ""
        counters.setdefault(source_category, 0)

        for line in md.read_text(encoding="utf-8", errors="replace").splitlines():
            source_subcategory = current_subcategory(line, source_subcategory)
            parsed = parse_markdown_row(line)
            if not parsed: continue

            # Preserve TOSEM source rows exactly. TOSEM has 116 rows
            # and 115 unique category/slug pairs because 1 OLAS finding appears 2x
            counters[source_category] += 1
            oracle_id = ("TOSEM-RC-" + re.sub(r"[^A-Z0-9]+", "-", source_category.upper()).strip("-") + f"-{counters[source_category]:03d}")
            row = {
                "oracle_id": oracle_id,
                "source_dataset": "TOSEM",
                "source_category": source_category,
                "source_subcategory": source_subcategory,
                "raw_line": clean_cell(line),
                "source_file": str(md),
                **parsed,
            }
            rows.append(row)

    return rows

def write_csv(path: Path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        for row in rows: w.writerow({c: row.get(c, "") for c in columns})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tosem-repo", default="external/SolidityStateStudy", help="Path to cloned HumblePLSE/SolidityStateStudy repo.")
    ap.add_argument("--out-raw", default="oracle/tosem_seed_raw.csv")
    args = ap.parse_args()
    tosem_repo = Path(args.tosem_repo)
    raw_rows = build_rows(tosem_repo)

    write_csv(Path(args.out_raw), raw_rows, RAW_COLUMNS)

    print(f"[OK] Parsed TOSEM root-cause rows: {len(raw_rows)}")
    print(f"[OK] Wrote {args.out_raw}")

    by_cat = {}
    for r in raw_rows: by_cat[r["source_category"]] = by_cat.get(r["source_category"], 0) + 1
    print("[SUMMARY] Rows by root-cause category:")
    for cat, n in sorted(by_cat.items()): print(f"  {cat}: {n}")

if __name__ == "__main__": main()

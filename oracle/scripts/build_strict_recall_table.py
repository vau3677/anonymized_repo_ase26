#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv
from collections import defaultdict
from pathlib import Path

FIELDS = [
    "source_pool",
    "web3bugs_id",
    "contest_slug",
    "mvbench_sheet",
    "oracle_rows_total",
    "mvsi_denominator",
    "strict_b0_matches",
    "strict_b0_false_negatives",
    "strict_recall",
    "strict_recall_decimal",
    "strict_recall_pct",
    "notes",
]

def load_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f: return list(csv.DictReader(f))

def require_columns(rows: list[dict[str, str]], path: str, columns: set[str]) -> None:
    if not rows:
        raise ValueError(f"{path} has no rows")
    missing = columns - set(rows[0])
    if missing:
        raise ValueError(f"{path} is missing required columns: {', '.join(sorted(missing))}")

def require_review_columns(rows: list[dict[str, str]], path: str) -> None:
    header = set(rows[0])
    if not ({"annotator_1_semantic_label", "annotator_1_strict_b0_match"} <= header or {"semantic_label", "strict_b0_match"} <= header):
        raise ValueError(
            f"{path} must include annotator_1_semantic_label/annotator_1_strict_b0_match "
            "or legacy semantic_label/strict_b0_match columns"
        )

def recall_fields(matches: int, denominator: int):
    if denominator == 0: return "NA", "NA", "NA"
    value = matches / denominator
    return f"{matches}/{denominator}", f"{value:.3f}", f"{value * 100:.1f}%"

def aggregate_row(source_pool, web3bugs_id, contest_slug, mvbench_sheet, rows, notes):
    denominator = sum(1 for row in rows if semantic_label(row) == "MV-SI")
    matches = sum(1 for row in rows if semantic_label(row) == "MV-SI" and strict_b0_match(row) == "yes")
    false_negatives = denominator - matches
    recall, decimal, pct = recall_fields(matches, denominator)
    return {
        "source_pool": source_pool,
        "web3bugs_id": web3bugs_id,
        "contest_slug": contest_slug,
        "mvbench_sheet": mvbench_sheet,
        "oracle_rows_total": str(len(rows)),
        "mvsi_denominator": str(denominator),
        "strict_b0_matches": str(matches),
        "strict_b0_false_negatives": str(false_negatives),
        "strict_recall": recall,
        "strict_recall_decimal": decimal,
        "strict_recall_pct": pct,
        "notes": notes,
    }

def group_rows(rows, key_fields):
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(field, "") for field in key_fields)].append(row)
    return grouped

def int_key(value: str):
    try: return int(value.split(";", 1)[0])
    except ValueError: return 10**9

def subtotal_row(source_pool: str, contest_slug: str, rows: list[dict[str, str]], notes: str) -> dict[str, str]:
    return aggregate_row(source_pool, "", contest_slug, "multiple", rows, notes)

def semantic_label(row: dict[str, str]) -> str:
    return (row.get("annotator_1_semantic_label") or row.get("semantic_label") or "").strip()

def strict_b0_match(row: dict[str, str]) -> str:
    return (row.get("annotator_1_strict_b0_match") or row.get("strict_b0_match") or "").strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tosem", default="oracle/tosem_oracle_review_queue.csv")
    parser.add_argument("--web3bugs", default="oracle/web3bugs_mvbench_review_queue.csv")
    parser.add_argument("--out", default="oracle/known_bug_strict_recall_table.csv")
    args = parser.parse_args()

    tosem_rows = load_csv(Path(args.tosem))
    web3bugs_rows = load_csv(Path(args.web3bugs))
    require_columns(tosem_rows, args.tosem, {"web3bugs_ids", "repo_slug", "mvbench_candidate_sheets"})
    require_columns(web3bugs_rows, args.web3bugs, {"web3bugs_id", "contest_slug", "mvbench_sheet"})
    require_review_columns(tosem_rows, args.tosem)
    require_review_columns(web3bugs_rows, args.web3bugs)
    output_rows: list[dict[str, str]] = []

    tosem_groups = group_rows(tosem_rows, ("web3bugs_ids", "repo_slug", "mvbench_candidate_sheets"))
    for (web3bugs_id, contest_slug, mvbench_sheet), rows in sorted(tosem_groups.items(), key=lambda item: int_key(item[0][0])):
        output_rows.append(
            aggregate_row("TOSEM-overlap", web3bugs_id, contest_slug, mvbench_sheet, rows, "Per-contest TOSEM overlap breakdown; manual semantic labels were assigned independently of MV-Bench output.")
        )

    web3bugs_groups = group_rows(web3bugs_rows, ("web3bugs_id", "contest_slug", "mvbench_sheet"))
    for (web3bugs_id, contest_slug, mvbench_sheet), rows in web3bugs_groups.items():
        output_rows.append(
            aggregate_row("Web3Bugs-Code4rena-complement", web3bugs_id, contest_slug, mvbench_sheet, rows, "Per-repository Web3Bugs/Code4rena complement breakdown; source-of-truth labels come from known findings, not MV-Bench.")
        )

    output_rows.append(
        subtotal_row("Web3Bugs-Code4rena-complement subtotal", "all complement repos", web3bugs_rows, "Subtotal for all manually audited Web3Bugs/Code4rena complement repositories.")
    )
    output_rows.append(
        subtotal_row("Combined independent oracle", "TOSEM overlap + Web3Bugs/Code4rena complement", tosem_rows + web3bugs_rows, "Paper-facing strict known-MVSI recall denominator. This is the headline row.")
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"[OK] Wrote {out_path} with {len(output_rows)} rows")

if __name__ == "__main__": main()

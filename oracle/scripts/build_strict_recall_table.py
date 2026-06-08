#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
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


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def recall_fields(matches: int, denominator: int) -> tuple[str, str, str]:
    if denominator == 0:
        return "NA", "NA", "NA"
    value = matches / denominator
    return f"{matches}/{denominator}", f"{value:.3f}", f"{value * 100:.1f}%"


def aggregate_row(
    source_pool: str,
    web3bugs_id: str,
    contest_slug: str,
    mvbench_sheet: str,
    rows: list[dict[str, str]],
    notes: str,
) -> dict[str, str]:
    denominator = sum(1 for row in rows if row.get("semantic_label") == "MV-SI")
    matches = sum(
        1
        for row in rows
        if row.get("semantic_label") == "MV-SI" and row.get("strict_b0_match") == "yes"
    )
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


def group_rows(rows: list[dict[str, str]], key_fields: tuple[str, ...]) -> dict[tuple[str, ...], list[dict[str, str]]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(field, "") for field in key_fields)].append(row)
    return grouped


def int_key(value: str) -> int:
    try:
        return int(value.split(";", 1)[0])
    except ValueError:
        return 10**9


def subtotal_row(source_pool: str, contest_slug: str, rows: list[dict[str, str]], notes: str) -> dict[str, str]:
    return aggregate_row(source_pool, "", contest_slug, "multiple", rows, notes)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tosem", default="oracle/audits/tosem_oracle_review_queue.csv")
    parser.add_argument("--web3bugs", default="oracle/web3bugs_mvbench_review_queue.csv")
    parser.add_argument("--out", default="oracle/known_bug_strict_recall_table.csv")
    args = parser.parse_args()

    tosem_rows = load_csv(Path(args.tosem))
    web3bugs_rows = load_csv(Path(args.web3bugs))

    output_rows: list[dict[str, str]] = []

    tosem_groups = group_rows(tosem_rows, ("web3bugs_ids", "repo_slug", "mvbench_candidate_sheets"))
    for (web3bugs_id, contest_slug, mvbench_sheet), rows in sorted(
        tosem_groups.items(), key=lambda item: int_key(item[0][0])
    ):
        output_rows.append(
            aggregate_row(
                "TOSEM-overlap",
                web3bugs_id,
                contest_slug,
                mvbench_sheet,
                rows,
                "Per-contest TOSEM overlap breakdown; semantic labels adjudicated independently of MV-Bench output.",
            )
        )

    web3bugs_groups = group_rows(web3bugs_rows, ("web3bugs_id", "contest_slug", "mvbench_sheet"))
    for (web3bugs_id, contest_slug, mvbench_sheet), rows in web3bugs_groups.items():
        output_rows.append(
            aggregate_row(
                "Web3Bugs-Code4rena-complement",
                web3bugs_id,
                contest_slug,
                mvbench_sheet,
                rows,
                "Per-repository Web3Bugs/Code4rena complement breakdown; source-of-truth labels come from known findings, not MV-Bench.",
            )
        )

    output_rows.append(
        subtotal_row(
            "Web3Bugs-Code4rena-complement subtotal",
            "all complement repos",
            web3bugs_rows,
            "Subtotal for all manually audited Web3Bugs/Code4rena complement repositories.",
        )
    )
    output_rows.append(
        subtotal_row(
            "Combined independent oracle",
            "TOSEM overlap + Web3Bugs/Code4rena complement",
            tosem_rows + web3bugs_rows,
            "Paper-facing strict known-MVSI recall denominator. This is the headline row.",
        )
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"[OK] Wrote {out_path} with {len(output_rows)} rows")


if __name__ == "__main__":
    main()

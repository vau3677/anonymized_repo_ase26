#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

FIELDS = [
    "oracle_id",
    "finding_slug",
    "repo_slug",
    "finding_id_norm",
    "source_category",
    "web3bugs_ids",
    "web3bugs_basis",
    "mvbench_status",
    "mvbench_candidate_sheets",
    "finding_match_count",
    "b0_match_count",
    "matched_ablations",
    "matched_types",
    "source_root_cause",
    "source_exploitation_method",
    "mvbench_b0_rows",
    "mvbench_all_matched_rows",
    "semantic_label",
    "mvsi_subtype",
    "violated_invariant",
    "evidence_source",
    "coupled_state_entities",
    "primary_state_entity",
    "counterpart_state_entity",
    "external_proxy_state",
    "desynchronization_step",
    "sink_type",
    "impact_type",
    "attacker_model",
    "strict_b0_match",
    "matched_b0_bucket_id",
    "fn_reason",
    "strict_match_notes",
]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize_join_row(row: dict[str, str]) -> str:
    return " | ".join(
        [
            f"sheet={row.get('matched_sheet', '')}",
            f"row={row.get('mvbench_row_idx', '')}",
            f"abl={row.get('mvbench_ablation', '')}",
            f"type={row.get('mvbench_type', '')}",
            f"finding={row.get('mvbench_finding', '')}",
            f"report={row.get('mvbench_code4rena_report', '')}",
            f"comments={row.get('mvbench_comments', '')}",
        ]
    )


def build_review_template(summary_rows: list[dict[str, str]], join_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    joined_by_oracle: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in join_rows:
        if row.get("mvbench_status") == "finding_match":
            joined_by_oracle[row["oracle_id"]].append(row)

    review_rows = []
    for row in summary_rows:
        if row["mvbench_status"] not in {"finding_match", "repo_sheet_no_finding"}:
            continue

        matches = joined_by_oracle.get(row["oracle_id"], [])
        b0_matches = [match for match in matches if match.get("mvbench_ablation") == "B0"]
        out = {field: row.get(field, "") for field in FIELDS}
        out["mvbench_b0_rows"] = "\n\n---\n\n".join(summarize_join_row(match) for match in b0_matches)
        out["mvbench_all_matched_rows"] = "\n\n---\n\n".join(summarize_join_row(match) for match in matches)
        out["semantic_label"] = "unlabeled"
        out["mvsi_subtype"] = "NA"
        out["evidence_source"] = "TOSEM root-cause row; Code4rena/Web3Bugs report; MV-Bench workbook overlap evidence"
        out["strict_b0_match"] = "not_checked"
        review_rows.append(out)

    return review_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a blank TOSEM review template from scripts/overlap.py outputs. "
            "This script is not the canonical reviewed queue; "
            "oracle/audits/tosem_oracle_review_queue.csv contains adjudicated labels."
        )
    )
    parser.add_argument("--summary", default="oracle/tosem_web3bugs_mvbench_summary.csv")
    parser.add_argument(
        "--join",
        default="oracle/tosem_web3bugs_mvbench_join.csv",
        help="Transient detailed join CSV produced by oracle/scripts/overlap.py.",
    )
    parser.add_argument("--out", default="oracle/audits/tosem_oracle_review_queue_template.csv")
    parser.add_argument("--force", action="store_true", help="Allow overwriting an existing output file.")
    args = parser.parse_args()

    summary_path = Path(args.summary)
    join_path = Path(args.join)
    out_path = Path(args.out)

    if out_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing output without --force: {out_path}")

    review_rows = build_review_template(load_csv(summary_path), load_csv(join_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"[OK] Wrote {out_path} with {len(review_rows)} review rows")


if __name__ == "__main__":
    main()

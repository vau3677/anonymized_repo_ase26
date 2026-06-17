# Oracle Schema

This file documents the current oracle artifacts. The strict recall inputs are complete; Annotator 2 labels are collected separately through the blind packet.

## Canonical Strict Recall Tables

### `oracle/tosem_oracle_review_queue.csv`

One row per manually reviewed TOSEM overlap finding. Core source and overlap fields:

- `oracle_id`
- `finding_slug`
- `repo_slug`
- `finding_id_norm`
- `source_category`
- `web3bugs_ids`
- `web3bugs_basis`
- `mvbench_status`
- `mvbench_candidate_sheets`
- `finding_match_count`
- `b0_match_count`
- `matched_ablations`
- `matched_types`
- `source_root_cause`
- `source_exploitation_method`
- `evidence_source`
- `mvbench_b0_rows`
- `mvbench_all_matched_rows`

Manual review and strict recall fields:

- `annotator_1_semantic_label`
- `annotator_1_mvsi_subtype`
- `annotator_1_strict_b0_match`
- `annotator_1_matched_b0_bucket_id`
- `annotator_1_fn_reason`
- `annotator_1_notes`

### `oracle/web3bugs_mvbench_review_queue.csv`

One row per reviewed Web3Bugs/Code4rena complement finding. Core source fields:

- `web3bugs_id`
- `mvbench_sheet`
- `oracle_id`
- `source_dataset`
- `source_category`
- `source_subcategory`
- `reporting_time`
- `bug_link`
- `finding_slug`
- `contest_slug`
- `finding_id`
- `project_slug`
- `finding_title`
- `source_root_cause`
- `source_exploitation_method`
- `source_fix_strategy`
- `evidence_source`
- `overlaps_mvscan_eval_repo`
- `mvbench_candidate_rows`

Manual review and strict recall fields:

- `annotator_1_semantic_label`
- `annotator_1_mvsi_subtype`
- `annotator_1_strict_b0_match`
- `annotator_1_matched_b0_bucket_id`
- `annotator_1_fn_reason`
- `annotator_1_notes`

`annotator_1_notes` preserves the compact rationale previously held in separate A1-only columns, including invariant, coupled entities, desynchronization step, sink, impact, attacker model, label notes, and strict-match notes when available.

## Generated Tables

- `oracle/known_bug_strict_recall_table.csv`: generated strict recall summary.

## A1 Reliability Source Tables

These checked-in CSVs contain Annotator 1 labels and rationales for reliability checks that are not part of the known-bug strict recall numerator/denominator.

### `oracle/zero_day_annotation_reliability.csv`

One row per candidate zero-day detector finding:

- `finding_key`
- `sheets`
- `ablations`
- `representative_row_idx`
- `finding_kind`
- `finding_header`
- `evidence_excerpt`
- `annotator_1_zero_day_status`
- `annotator_1_semantic_label`
- `annotator_1_notes`

`annotator_1_zero_day_status` uses `confirmed-zero-day`, `duplicate-known-bug`, `not-a-bug`, `insufficient-evidence`, or `out-of-scope`.

### `oracle/b0_stratified_sample_reliability.csv`

One row per stratified B0 alert sample:

- `sample_id`
- `sample_seed`
- `stratum_kind`
- `sheet`
- `row_idx`
- `finding_key`
- `finding_header`
- `evidence_excerpt`
- `annotator_1_b0_label`
- `annotator_1_semantic_label`
- `annotator_1_notes`

`annotator_1_b0_label` uses `TP`, `FP`, or `ambiguous`. The original sample stratum is not treated as authoritative; A1 labels are the independent reviewed decision.

## Annotator 2 Blind Packet

- `oracle/annotator2_packet/known_bug_review_blind.csv`
- `oracle/annotator2_packet/zero_day_review_blind.csv`
- `oracle/annotator2_packet/b0_sample_review_blind.csv`

These checked-in files intentionally exclude A1 labels, current semantic labels, strict B0 decisions, matched bucket IDs, false-negative reasons, and recall summaries. Annotator 2 should receive only the files in `oracle/annotator2_packet/`.

## Semantic Labels

`annotator_1_semantic_label` and `annotator_2_semantic_label` use:

- `MV-SI`
- `SV-SI`
- `ISU-other`
- `other-logical-bug`
- `ambiguous`
- `excluded`

Label `MV-SI` if and only if all of the following hold:

1. There are `n >= 2` semantically coupled state entities.
2. Coupling is justified by independent evidence such as a protocol invariant, bug report, accounting equation, developer note, or developer rule.
3. An execution path updates, advances, invalidates, or consumes one constituent without synchronizing at least one required counterpart.
4. The stale or inconsistent counterpart reaches a security- or economically-relevant sink.
5. The defect is not reducible to a same-variable stale read, reentrancy, ordinary missing access control, or arithmetic error.

Label `SV-SI` for same-variable stale or inconsistent-state issues without a multi-entity relational invariant.

Label `ISU-other` for inconsistent-state-update issues that are broader than, or distinguishable from, `MV-SI` and `SV-SI`.

## Strict B0 Matching Rule

Let `o` be an oracle bug and `b` be an MV-Scan B0 bucket. `b` strictly matches `o` if and only if all of the following hold:

1. Same evaluated repository.
2. Same violated invariant.
3. Same or directly specialized coupled state group.
4. Same desynchronization step.
5. Same sink decision class.

This is stricter than ordinary semantic similarity. A bucket is not a strict match merely because it appears in the same repository, mentions one overlapping state entity, or reaches the same broad sink type.

The reported metric is:

```text
strict known-MVSI recall_B0 =
| known MV-SI oracle cases strictly matched by B0 |
/
| known MV-SI oracle cases in evaluated repositories |
```

## Diagnostic B0 Overlap

Diagnostic overlap may be used for false-negative explanation and artifact debugging, but it is not part of the main recall number.

# Annotator 2 Blind Packet

This is the only oracle material intended for Annotator 2 (A2) during the independent annotation pass. Since this is blind, do not inspect the rest of `oracle/` before completing these files. Fill only blank `annotator_2_*` columns. Do not edit anything that is already filled.

Complete the files in this order: 1. `known_bug_review_blind.csv`, 2. `zero_day_review_blind.csv`, 3. `b0_sample_review_blind.csv`.

## Shared MV-SI Litmus

Use this same litmus for every file and only label `MV-SI` when C1-C5 all pass:

- C1: `>=2` semantically coupled state entities.
- C2: Coupling is justified by independent evidence.
- C3: One constituent is updated, advanced, invalidated, or consumed without synchronizing a required counterpart.
- C4: The stale or inconsistent counterpart reaches a security- or economically-relevant sink.
- C5: The defect is not reducible to same-variable stale read, reentrancy, ordinary access control, or arithmetic/formula-only error.

## 1. `known_bug_review_blind.csv`

We independently label each known bug and decide whether B0 strictly matched it. Fill these columns:

- `annotator_2_semantic_label` options are: `MV-SI`, `SV-SI`, `ISU-other`, `other-logical-bug`, `ambiguous`, `excluded`.
  - `MV-SI` only when C1-C5 all pass.
  - `SV-SI` for same-variable stale/inconsistent-state bugs.
  - `ISU-other` for SI bugs that are not cleanly MV-SI or SV-SI.
  - `other-logical-bug` for real bugs outside this taxonomy.
  - `ambiguous` for insufficient evidence.
  - `excluded` for duplicate/out-of-scope/broken-source/not-real-finding rows.

- `annotator_2_mvsi_subtype` options are: `Type-I-temporal-checkpoint`, `Type-II-asset-utility`, `Type-III-governance-config`, `other-MVSI`, `NA`.
  - Use `NA` when `annotator_2_semantic_label` is not `MV-SI`.

- `annotator_2_strict_b0_match` options are: `yes`, `no`, `not_applicable`, `ambiguous`.
  - Use `not_applicable` unless `annotator_2_semantic_label` is `MV-SI`.
  - Use `yes` only when a B0 candidate has the same evaluated repo, same violated invariant, same or directly specialized coupled state group, same desynchronization step, and same sink decision class.
  - Use `no` when the row is MV-SI but no B0 candidate strictly matches.

- `annotator_2_matched_b0_bucket_id`: if strict match is `yes`, write `<sheet>:B0:row<row_idx>`, and otherwise use `NA-no-strict-B0-match`, `NA-not-MVSI`, or `NA-ambiguous`.
- `annotator_2_fn_reason`: options include `NA-not-MVSI`, `NA-strict-B0-match`, `FN0-no-same-finding-tag-row`, `FN1-same-finding-tag-not-in-B0`, `FN7-bucket-adjacent-not-strict`, `FN-other (<short reason>)`, `ambiguous`.
- `annotator_2_notes`: edit on hard rows (e.g., `C1=<pass/fail/unclear>; C2=<pass/fail/unclear>; C3=<pass/fail/unclear>; C4=<pass/fail/unclear>; C5=<pass/fail/unclear> | rationale=<1-2 sentences>`) and put invariant/entities/sink details here for adjudication.

## 2. `zero_day_review_blind.csv`

We then independently confirm zero-day status and assign the same semantic taxonomy. Fill only these columns:

- `annotator_2_zero_day_status` options are: `confirmed-zero-day`, `duplicate-known-bug`, `not-a-bug`, `insufficient-evidence`, `out-of-scope`.
- `annotator_2_semantic_label` options: `MV-SI`, `SV-SI`, `ISU-other`, `other-logical-bug`, `ambiguous`, `excluded`.
- `annotator_2_notes` are optional but recommended for anything other than a basic confirmation, and we can include the C1-C5 result and why the candidate is/isn't a zero-day.

## 3. `b0_sample_review_blind.csv`

Lastly, we do an independent audit of sampled B0 alerts as detector TP/FP labels. The original TP/FP stratum is hidden. Fill only these three columns:

- `annotator_2_b0_label` options: `TP`, `FP`, `ambiguous`.
  - `TP`: independent evidence confirms a real security/economic issue and the B0 alert captures the relevant stale/inconsistent-state behavior.
  - `FP`: no confirmed bug, benign relation, detector-only relation, wrong behavior/sink, or non-security issue.

- `annotator_2_semantic_label` options: `MV-SI`, `SV-SI-or-same-variable-SI`, `ISU-other`, `not-confirmed-alert`, `ambiguous`, `excluded`.
- `annotator_2_notes` is optional but recommended for FP/ambiguous rows and you can do it in this format: `C1=<pass/fail/unclear>; C2=<pass/fail/unclear>; C3=<pass/fail/unclear>; C4=<pass/fail/unclear>; C5=<pass/fail/unclear> | rationale=<one or two sentences>`
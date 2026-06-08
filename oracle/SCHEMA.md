# Oracle Schema

> Each row is one known bug from TOSEM/Web3Bugs.

## Core source metadata

- `oracle_id`: stable local identifier
- `source_dataset`: `TOSEM`, `Web3Bugs`, or `Code4rena`
- `source_category`: original source category (e.g. `Dynamic Dependent Update Omission`)
- `source_subcategory`: optional source subtype
- `reporting_time`: date reported by source
- `bug_link`: link to the Code4rena or Github finding
- `finding_slug`: slug (e.g. `2021-12-vader#h-10`)
- `contest_slug`: contest part (e.g. `2021-12-vader`)
- `finding_id`: finding id (e.g. `h-10`)
- `project_slug`: normalized project name (e.g. `vader`)
- `finding_title`: short title derived from the source if available

## Source evidence

- `source_root_cause`: original source root-cause summary
- `source_exploitation_method`: original source exploitation summary
- `source_fix_strategy`: original source fix summary
- `evidence_source`: bug report, fix diff, code comment, docs, PoC, vendor confirmation, etc.

## MV-SI semantic labeling

- `semantic_label`: one of `MV-SI`, `SV-SI`, `ISU-other`, `other-logical-bug`, `ambiguous`, `excluded`.
- `mvsi_subtype`: `Type-I-temporal-checkpoint`, `Type-II-asset-utility`, `Type-III-governance-config`, `other-MVSI`, or `NA`.
- `violated_invariant`: relational invariant in prose.
- `coupled_state_entities`: comma-separated state variables, slots, or external proxies.
- `primary_state_entity`: source-of-truth state entity if identifiable.
- `counterpart_state_entity`: stale/cached/redundant counterpart if identifiable.
- `external_proxy_state`: remote/cross-contract state if applicable.
- `desynchronization_step`: operation/path that updates/consumes one constituent without synchronizing counterpart.
- `sink_type`: branch, accounting, external-call, storage-write, mint, burn, transfer, liquidation, reward, governance, access-control, other.
- `impact_type`: loss, DoS, overmint, underpayment, overpayment, governance, accounting, other.
- `attacker_model`: unprivileged, privileged, governance, unclear.

## Evaluation overlap and strict recall

- `overlaps_mvscan_eval_repo`: yes/no/maybe.
- `matched_eval_label`: matching label from MV-Scan evaluated repo ledger.
- `strict_b0_match`: yes/no/not_checked.
- `matched_b0_bucket_id`: stable MV-Scan bucket/finding key if matched.
- `fn_reason`: internal strict-match category. MV-SI misses use `FN0-*`, `FN1-*`, `FN7-*`, etc.; strict matches use `NA-strict-B0-match`; non-MV-SI rows use `NA-not-MVSI`.

## Annotation

- `annotator_1_label`
- `annotator_2_label`
- `adjudicated_label`
- `adjudication_notes`
- `notes`

## B0 matching rules

1. `strict_B0_match`: the main paper should only report this
2. `diagnostic_B0_overlap`: used internally for near-miss analysis, debugging, and relaxed artifact diagnostics.

## Strict B0 matching rule

Let `o` be an oracle bug and `b` be an MV-Scan B0 bucket. `b` strictly matches `o` if and only if all of the following hold:

1. Same evaluated repository.
2. Same violated invariant.
3. Same or directly specialized coupled state group.
4. Same desynchronization step.
5. Same sink decision class.

This is intentionally stricter than ordinary semantic similarity. A bucket should not be counted as a strict match merely because it appears in the same repository, mentions one overlapping state entity, or reaches the same broad sink type. The main paper reports:

```text
strict known-MVSI recall_B0 =
| known MV-SI oracle cases strictly matched by B0 |
/
| known MV-SI oracle cases in evaluated repositories |
```

## Diagnostic B0 overlap rule

> Diagnostic overlap is used for artifact analysis and false-negative explanation, not for the main recall number.

Let `o` be an oracle bug and `b` be an MV-Scan B0 bucket. `b` has diagnostic overlap with `o` if all of the following hold:

1. `o` and `b` come from the same evaluated repository.
2. The invariant violated by `o` is the same as, related to, or a direct specialization of the invariant represented by `b`.
3. At least one state variable, mapping slot, or external proxy in `o` appears in `b`'s entangled group.
4. `b` identifies at least one writer, reader, or transaction step involved in the known exploit or bug trace.
5. `b`'s stale-read sink corresponds to the same class of protocol decision: branch, accounting update, external call, storage write, mint, burn, transfer, liquidation, reward, governance, or access-control decision.

Diagnostic overlap distinguishes: (i) strict true matches, (ii) near misses where MV-Scan found the right state group but not the right path, (iii) near misses where MV-Scan found the right sink class but not the full invariant, (iv) false negatives caused by coarse bucketing, and (v) unrelated same-repository alerts.

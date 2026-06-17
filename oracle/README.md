# Oracle Construction

This folder contains the independent known-bug oracle used for strict MV-SI B0 recall. The strict recall metric is complete. The annotation-reliability pass is not complete as Annotator 2 has not started.

## Current Status

### Strict B0 Recall

- TOSEM seed rows parsed: 116
- TOSEM rows mapped into evaluated MV-Bench sheets and manually reviewed: 15
- Web3Bugs/Code4rena complement rows manually reviewed: 140
- Combined reviewed oracle rows: 155
- Combined MV-SI denominator rows: 46
- Combined strict B0 matches: 7
- Combined strict B0 recall: 7 / 46 = 0.152
- Recall table: `oracle/known_bug_strict_recall_table.csv`

The strict recall table is generated from the canonical review queues using `annotator_1_semantic_label` for the denominator and `annotator_1_strict_b0_match` for the numerator. Annotator 2 labels are collected separately through the checked-in blind packet.

### Annotation Reliability

Incomplete because Annotator 2 has not started. The A1 reliability source files are checked in and ready for adjudication after A2:

- `oracle/zero_day_annotation_reliability.csv`
- `oracle/b0_stratified_sample_reliability.csv`

Use only the blind packet in `oracle/annotator2_packet/` for Annotator 2. Do not send the full `oracle/` folder until after Annotator 2 finishes, because the full folder contains A1 labels, strict B0 decisions, matched bucket IDs, false-negative reasons, and recall summaries.

### TOSEM Alignment

| Reviewed TOSEM class | Cases |
| --- | ---: |
| MV-SI | 9 |
| SV-SI / same-variable | 6 |
| ISU-other | 0 |
| Other / not applicable | 0 |
| Excluded | 0 |
| Total reviewed | 15 |

## Main Artifacts

- `tosem_seed_raw.csv`: parsed TOSEM seed rows.
- `tosem_web3bugs_mvbench_summary.csv`: TOSEM-to-Web3Bugs-to-MV-Bench overlap summary.
- `tosem_oracle_review_queue.csv`: canonical TOSEM manual semantic review rows used for strict recall.
- `web3bugs_mvbench_review_queue.csv`: canonical Web3Bugs/Code4rena complement rows with MV-Bench candidate matching evidence.
- `zero_day_annotation_reliability.csv`: A1 zero-day confirmation and semantic labels for candidate zero-day detector findings.
- `b0_stratified_sample_reliability.csv`: A1 TP/FP audit for the stratified B0 alert sample.
- `known_bug_strict_recall_table.csv`: generated strict known-MVSI recall table.
- `annotator2_packet/`: blind packet for Annotator 2.
- `SCHEMA.md`: oracle schema, label definitions, and strict B0 matching rule.

## Reproduction

1. Parse TOSEM rows:
   `python3 oracle/scripts/build_tosem_seed.py`
2. Regenerate TOSEM overlap summary and transient join:
   `python3 oracle/scripts/overlap.py --out oracle/tosem_web3bugs_mvbench_join.csv`
3. If rebuilding a blank TOSEM review template:
   `python3 oracle/scripts/make_tosem_review_queue.py`
4. Regenerate strict recall table:
   `python3 oracle/scripts/build_strict_recall_table.py`

The transient `oracle/tosem_web3bugs_mvbench_join.csv` is an intermediate rebuild artifact, not a canonical reviewed table.

## Semantic Labels

A finding is `MV-SI` if and only if:

1. There exist `n >= 2` semantically coupled state entities `v_1, v_2, ..., v_n`.
2. The coupling is justified by an independent source like a protocol invariant, a bug report, an accounting equation, a developer note, or a developer rule.
3. There exists an execution path that updates, advances, invalidates, or consumes one constituent without synchronizing at least one required counterpart.
4. The stale counterpart reaches a security or economically relevant sink, such as a branch predicate, external call, storage write, accounting update, mint, burn, transfer, liquidate, vote, emission, reward, or access decision.
5. The defect cannot be explained as a single-variable stale read, reentrancy, ordinary missing access control, or an arithmetic error.

A finding is `SV-SI` if it is a same-variable stale or inconsistent state issue without a multi-entity relational invariant.

An `ISU-other` finding is an inconsistent-state-update issue that is broader than, or distinguishable from, `MV-SI` and `SV-SI`.

Use `other-logical-bug` for real logical bugs that are not meaningfully classifiable as `SV-SI`, `MV-SI`, or `ISU-other`; `ambiguous` when the evidence is insufficient after review; and `excluded` for duplicates, broken-source findings, out-of-scope findings, or findings outside the evaluated repository.

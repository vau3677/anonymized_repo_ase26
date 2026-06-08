# Independent Oracle and Annotation Reliability Readiness Check

- Independent known-bug oracle is complete for strict B0 recall.
- The annotation-reliability package is not yet complete.

## Independent Oracle

### TOSEM seed pool

Complete for the seed-overlap pass.

- Source seed table: `oracle/tosem_seed_raw.csv`
- TOSEM seed cases: 116
- TOSEM cases mapped to Web3Bugs by report slug: 26
- TOSEM cases in evaluated MV-Bench sheets and manually reviewed: 15
- Reviewed TOSEM labels: see the compact TOSEM alignment table in `oracle/README.md`.
- Strict B0 matches among TOSEM MV-SI rows: 1 / 9

Relevant artifacts:

- `oracle/tosem_web3bugs_mvbench_summary.csv`
- `oracle/audits/tosem_oracle_review_queue.csv`
- `oracle/audits/TOSEM_manual_audit.md`

The TOSEM overlap review queue is the canonical source for the reviewed TOSEM semantic-label counts.

## Web3Bugs/Code4rena Complement

Because TOSEM seed pool overlap produced fewer than 30 MV-SI candidates, we complemented it with Web3Bugs known findings from our evaluated repos. We randomly select repos from our evaluated corpus and audit their corresponding Code4rena report for the same data as is present in TOSEM.

Randomly chosen repositories from the evaluated Web3Bugs corpus:

* `59`, `2021-11-malt`
* `104`, `2022-03-joyn`
* `60`, `2021-12-perennial`
* `72`, `2022-01-openleverage`
* `123`, `2022-05-aura`
* `41`, `2021-10-defiprotocol`

Total Web3Bugs oracle rows reviewed: 99 High and Medium

- MV-SI: 22
- SV-SI: 8
- ISU-other: 2
- other-logical-bug: 67
- Strict B0 matches among Web3Bugs MV-SI rows: 5/22

Relevant artifacts:

- `oracle/audits/web3bugs_semantic_label_audit.md`
- `oracle/web3bugs_mvbench_review_queue.csv`
- `oracle/audits/web3bugs_mvbench_manual_audit.md`

## Combined Strict Recall Denominator

Complete for the known-MVSI oracle denominator.

Paper-facing strict recall table:

- `oracle/known_bug_strict_recall_table.csv`
- generator: `oracle/scripts/build_strict_recall_table.py`

- TOSEM MV-SI denominator rows: 9
- Web3Bugs complement MV-SI denominator rows: 22
- Combined MV-SI denominator rows: 31
- Target: 30 reached

Strict B0 recall over the combined denominator:

- TOSEM strict B0 matches: 1
- Web3Bugs complement strict B0 matches: 5
- Combined strict B0 matches: 6
- Combined strict recall: 6 / 31 = 0.194

## Per-Case Fields

Status: mostly complete for oracle recall.

The current oracle rows include:

- violated invariant
- evidence source
- coupled state entities
- MV-SI / SV-SI / ISU-other / other-logical-bug label
- desynchronization step
- sink type
- impact type
- attacker model
- evaluated-repo overlap
- strict B0 match
- matched B0 bucket ID
- FN reason
- notes

The evidence source is independent of MV-Scan/MV-Bench and includes Code4rena reports, GitHub finding pages, local Web3Bugs report files, source files, judge comments, sponsor confirmations, and mitigation notes.

## Remaining Work

### Annotation

The following required paper-facing pieces are still missing:

- Known-bug oracle independent two-pass labels.
- Known-bug oracle adjudication sheet.
- Cohen's kappa/agreement calculation for known-bug labels.
- Independent two-pass confirmation for all zero-days.
- Cohen's kappa/agreement calculation for zero-day confirmation.
- Stratified B0 alert sample audit for TP/FP reliability.
- Cohen's kappa/agreement calculation for the B0 sample.

Artifacts to create:

1. `oracle/known_bug_annotation_reliability.csv`
   - One row per known-bug oracle case used in the paper-facing oracle.
   - Include annotator 1 label, annotator 2 label, adjudicated label, disagreement flag, and adjudication notes.

2. `oracle/known_bug_annotation_reliability.md`
   - Describe the two-pass process and report agreement / Cohen's kappa.

3. `oracle/zero_day_annotation_reliability.csv`
   - One row per claimed zero-day.
   - Include independent labels and adjudication.

4. `oracle/b0_stratified_sample_reliability.csv`
   - Stratified sample of B0 alerts for TP/FP audit.
   - Include sampling strata, both annotator labels, adjudication, and final label.

5. `oracle/annotation_reliability_summary.md`
   - Paper-ready summary of agreement, kappa, adjudication counts, and residual ambiguity.

Until those are created, the independent oracle is ready for strict known-bug recall, but the annotation-reliability requirement remains the main evaluation gap.

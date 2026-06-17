# Oracle Next Steps

The strict known-bug B0 recall oracle is complete. The annotation-reliability package is not complete because Annotator 2 has not started.

## Completed Strict Recall Work

### TOSEM Seed Pool

- Source seed table: `oracle/tosem_seed_raw.csv`
- TOSEM seed cases: 116
- TOSEM cases mapped to Web3Bugs by report slug: 26
- TOSEM cases in evaluated MV-Bench sheets and manually reviewed: 15
- Strict B0 matches among TOSEM MV-SI rows: 1 / 9
- Artifacts:
  - `oracle/tosem_web3bugs_mvbench_summary.csv`
  - `oracle/tosem_oracle_review_queue.csv`

### Web3Bugs/Code4rena Complement

Because the TOSEM seed-overlap pass produced fewer than 30 MV-SI cases, we added a repository-level complement from evaluated Web3Bugs repositories with complete Code4rena reports and corresponding MV-Bench sheets. For each selected repository, we reviewed all High/Medium findings under the same semantic schema used for the TOSEM overlap. Selection and labeling were performed before computing the final strict B0 recall headline, and no individual finding was included or excluded based on whether B0 matched it. Complement repositories from the evaluated Web3Bugs corpus:

- `59`, `2021-11-malt`
- `104`, `2022-03-joyn`
- `60`, `2021-12-perennial`
- `72`, `2022-01-openleverage`
- `123`, `2022-05-aura`
- `41`, `2021-10-defiprotocol`
- `107`, `2022-04-jpegd`
- `71`, `2022-01-insure`

Total Web3Bugs oracle rows reviewed: 140 High and Medium

- MV-SI: 37
- SV-SI: 14
- ISU-other: 2
- other-logical-bug: 87
- Strict B0 matches among Web3Bugs MV-SI rows: 6 / 37
- Full review queue is here: `oracle/web3bugs_mvbench_review_queue.csv`

### Combined Strict Recall

Paper-facing strict recall table is here: `oracle/known_bug_strict_recall_table.csv`
The generator is: `oracle/scripts/build_strict_recall_table.py`
Results:
  - TOSEM MV-SI denominator rows: 9
  - Web3Bugs complement MV-SI denominator rows: 37
  - Combined MV-SI denominator rows: 46
  - Combined strict B0 matches: 7
  - Combined strict recall: 7 / 46 = 0.152

## TODO

1. Complete A2 files with the `annotator_2_*` columns filled.
2. Merge A2 labels back into the reliability working files.
3. Adjudicate disagreements between A1/manual labels and A2 labels.
4. Compute agreement and Cohen's kappa for known-bug semantic labels, ZD confirmation labels, and B0 sample TP/FP labels.
5. Create final reliability artifacts:
   - `oracle/known_bug_annotation_reliability.csv`
   - `oracle/known_bug_annotation_reliability.md`
   - `oracle/annotation_reliability_summary.md`

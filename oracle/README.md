# Oracle Construction

This folder contains the independent known-bug oracle used for strict MVSI recall. Our oracle starts from known bugs, it labels each bug under the MV-SI taxonomy, and checks whether MV-Scan's B0 ablation produced a strict match to the confirmed finding. The oracle combines two source pools under one [schema](SCHEMA.md):

1. **TOSEM seed overlap.** We study their labeled repositories which overlap with MV-Bench's evaluated corpus. TOSEM had already provided root-cause, exploitation method, and fix-strategy machinery for many SI findings, so we used it directly when investigating recall.
2. **Web3Bugs/Code4rena.** Naturally, the TOSEM overlap was not large enough to conclusively determine recall. We then investigated additional High/Medium Code4rena findings from a random subset of evaluated Web3Bugs repositories until we hit our goal of 30 MV-SI labels. Web3Bugs/Code4rena required hand-labeling into the same MV-SI, SV-SI, ISU-other, and other-logical-bug fields in order to match the same level of rigor as TOSEM.

## Current Status

### Strict Oracle Results (complete)

- TOSEM seed rows parsed: 116
- TOSEM rows mapped into evaluated MV-Bench sheets and manually reviewed: 15
- Web3Bugs/Code4rena complement rows manually reviewed: 99
- Combined reviewed oracle rows: 114
- Combined MV-SI denominator rows: 31
- Combined strict B0 matches: 6
- Combined strict B0 recall: 6 / 31 = 0.194
- Recall table: `oracle/known_bug_strict_recall_table.csv` (it reports TOSEM overlap per contest, the Web3Bugs/Code4rena complement per repository, a Web3Bugs complement subtotal, and the combined headline row).

### TOSEM Alignment Table (complete)

| Reviewed TOSEM class | Cases |
| --- | ---: |
| MV-SI | 9 |
| SV-SI / same-variable | 6 |
| ISU-other | 0 |
| Other / not applicable | 0 |
| Excluded | 0 |
| Total reviewed | 15 |

### Annotation/Reliability Pass (incomplete) (see `NEXT_STEPS.md`)

- Two-pass labels
- Adjudication records
- Agreement statistics for the known-bug oracle
- Cohen's Kappa
- zero-day confirmation
- B0 TP/FP sample audit

### Artifacts

- `tosem_seed_raw.csv`: parsed TOSEM seed rows.
- `tosem_web3bugs_mvbench_summary.csv`: TOSEM-to-Web3Bugs-to-MV-Bench overlap summary.
- `audits/tosem_oracle_review_queue.csv`: adjudicated TOSEM overlap rows used for strict recall.
- `audits/TOSEM_manual_audit.md`: manual TOSEM overlap audit notes and strict-match decisions.
- `audits/web3bugs_semantic_label_audit.md`: consolidated Web3Bugs/Code4rena semantic-label audit notes.
- `web3bugs_mvbench_review_queue.csv`: canonical Web3Bugs/Code4rena complement rows with MV-Bench candidate matching evidence.
- `audits/web3bugs_mvbench_manual_audit.md`: manual complement audit notes and strict-match decisions.
- `known_bug_strict_recall_table.csv`: generated strict known-MVSI recall table.
- `scripts/build_strict_recall_table.py`: generator for `known_bug_strict_recall_table.csv`.
- `SCHEMA.md`: oracle schema and strict B0 matching rule.

## Reproduction Instructions

1. Parse TOSEM rows with `scripts/build_tosem_seed.py`.
2. Map TOSEM finding slugs to Web3Bugs IDs and candidate MV-Bench sheets with `scripts/overlap.py`.
3. If rebuilding from scratch, use `scripts/make_tosem_review_queue.py` to create a blank TOSEM review template from the transient detailed join emitted by `scripts/overlap.py`.
4. Manually adjudicate each known bug against the common semantic schema in the canonical review queues.
5. Apply the same semantic schema to the Web3Bugs/Code4rena complement.
6. Count only adjudicated `MV-SI` rows in evaluated repositories in the strict recall denominator.
7. Count a B0 match only when it satisfies the strict matching rule in `SCHEMA.md`.
8. Regenerate `known_bug_strict_recall_table.csv` with `scripts/build_strict_recall_table.py`.

## Semantic Labels

A finding is `MV-SI` if and only if:

1. There exist `n >= 2` semantically coupled state entities `v_1, v_2, ..., v_n`.
2. The coupling is justified by an independent source like a protocol invariant, a bug report, an accounting equation, a developer note, or a developer rule.
3. There exists an execution path that updates, advances, invalidates, or consumes 1 constituent without synchronizing `>= 1` required counterpart.
4. The stale counterpart reaches a security or economically relevant sink, such as a branch predicate, external call, storage write, accounting update, mint, burn, transfer, liquidate, vote, emission, reward, or access decision.
5. The defect cannot be explained as a single-variable stale read, reentrancy, ordinary missing access control, or an arithmetic error.

A finding is `SV-SI` if it is a same-variable stale or inconsistent state issue without a multi-entity relational invariant.

An `ISU-other` finding is an inconsistent-state-update issue that is broader than, or distinguishable from, `MV-SI` and `SV-SI`.

We use `other-logical-bug` for real logical bugs that are not meaningfully classifiable as `SV-SI`, `MV-SI`, or `ISU-other`; `ambiguous` when the evidence is insufficient after review; and `excluded` for duplicates, broken-source findings, out-of-scope findings, or findings outside the evaluated repository.

> The strict known-MVSI recall metric and matching criteria are in `SCHEMA.md`. Paper-facing counts are in `known_bug_strict_recall_table.csv`.

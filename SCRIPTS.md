# SCRIPTS.md — Script Reference

This document describes scripts in this repository: what they do, how they work internally, how to run them, and what they output.

---

## Table of Contents

- [dataset/main.py](#datasetmainpy)

---

## dataset/main.py

**Purpose:** Runs MV-Scan ablation study across a dataset of Solidity projects. It discovers contract project roots, infers the framework for each project, executes the detector once per ablation configuration, captures runtime/output artifacts, and records resumable TSV results alongside an `out/` dir with results.

**How it works:**

1. Resolves the dataset root from `--dataset-dir` and the contract subtree from `--contracts-subdir`.
2. Recursively scans for candidate project roots using `find_config_dirs()`. Keeps only directories containing a recognized framework config and respects the `SKIP_DIRS` filter.
3. Loads ablations and writes a stable ablation index.
4. Skips any project for which all requested ablations are already recorded.
5. For each project, infers the framework with `detect_framework()` with a fallback to `contracts/**/*.sol` or `src/**/*.sol`.
6. Starts from ```slither . --detect inconsistent_state```, appends framework-specific “ignore compile” and “force framework” flags (useful for debugging failed test runs).
7. For each ablation: injects the ablation env variables, sets `ISD_JSON_OUT` to the per-run JSON path, runs the command with timeout protection, captures stdout/stderr together, extracts the analyzer tail summary if present, and records elapsed runtime and return code.
8. For each project/ablation, writes `out/<label>/<ablation_id>/findings.json`, `out/<label>/<ablation_id>/slither_stdout.txt`, and `out/<label>/<ablation_id>/meta.json`.
9. Appends one summary line to the results TSV, namely:
```text
<label>    <ablation_name>    <status_line>    <elapsed_sec>    <rc>
```

**Usage:**

Basic usage (will work, but may fail on specific repos if automated compilation fails):

```bash
python3 main.py --dataset-dir ./Web3Bugs --contracts-subdir contracts
```

To isolate a failed test, first delete it from your `results.tsv` and run:

```bash
python3 main.py --only <repo> <env flags>
```

**Arguments:**
- `--dataset-dir` — dataset root (default: `./Web3Bugs`)
- `--contracts-subdir` — contract subtree under the dataset root (default: `contracts`)
- `--out-json` — declared JSON output name, though the current implementation writes fixed per-run `findings.json` paths
- `--cmd` — base detector command (default: `slither . --detect inconsistent_state`)
- `--timeout-run` — per-run timeout in seconds (default: `600`)
- `--only` — optional substring filter for project labels
- `--results-file` — resumable TSV output path (default: `out/done.tsv`)
- `--abl` — repeatable inline ablation specification
- `--abl-file` — JSON file containing ablation definitions

**Inputs:**
- A dataset directory containing Solidity project roots under the configured contracts subtree.
- A working Slither installation available on `PATH`.

**Outputs:**
- `out/ablation_map.json` — ablation ID/name/env mapping
- `out/ablation_map.tsv` — TSV version of the mapping
- `out/done.tsv` — resumable run ledger
- `out/<label>/<ablation_id>/findings.json` — per-run detector JSON
- `out/<label>/<ablation_id>/slither_stdout.txt` — full analyzer output
- `out/<label>/<ablation_id>/meta.json` — structured run metadata

**Default ablations:**
- `baseline`
- `no_init_only`
- `no_admin_benign`
- `sink_none`
- `sink_samevar`
- `budget_0`
- `budget_inf`

**Important notes:**

- If the script fails, the reason will still be written to `out/<label>/<ablation_id>/`, primarily evident in `slither_stdout.txt`.
- The two main blockers for successfully running the detector on a repo is (a) a failed compilation or (b) a working compilation that does not track `storageLayout`.
- Tracks successful runtime samples by ablation and overall.
- Prints average runtimes at the end, or after interruption.
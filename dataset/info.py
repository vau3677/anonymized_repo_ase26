import os, argparse, math, statistics
from pathlib import Path
from collections import defaultdict, Counter

def list_out(out_dir):
    ids = []
    for name in os.listdir(out_dir):
        if name.isdigit(): ids.append(name)
    return sorted(ids, key=lambda j: int(j))

def scan_repo(repo_dir, exts):
    file_locs, file_sizes, file_records, pragma_versions = [], [], [], set()

    for root, _, files in os.walk(repo_dir):
        for f in files:
            lf = f.lower()
            if not any(lf.endswith(ext) for ext in exts): continue

            fullp = Path(root) / f
            loc_nonempty = 0
            pragma_found = None

            try:
                with open(fullp, "r", errors="ignore") as fh:
                    for line in fh:
                        stripped = line.strip()
                        if stripped: loc_nonempty += 1
                        if pragma_found is None and stripped.startswith("pragma solidity"):
                            semi = stripped.find(";")
                            if semi != -1: pragma_found = stripped[:semi + 1]
                            else: pragma_found = stripped
            except OSError:
                loc_nonempty, pragma_found = 0, None

            try: size_bytes = fullp.stat().st_size
            except OSError: size_bytes = 0

            file_locs.append(loc_nonempty)
            file_sizes.append(size_bytes)
            file_records.append((str(fullp.relative_to(repo_dir)), loc_nonempty, size_bytes))

            if pragma_found: pragma_versions.add(pragma_found)

    cnt_files = len(file_locs)
    total_loc = sum(file_locs)
    avg_loc = (total_loc // cnt_files) if cnt_files else 0
    med_loc = int(statistics.median(file_locs)) if file_locs else 0
    max_loc = max(file_locs) if file_locs else 0
    max_kb = (max(file_sizes) // 1024) if file_sizes else 0

    return {
        "cnt_files": cnt_files,
        "total_loc": total_loc,
        "avg_loc": avg_loc,
        "med_loc": med_loc,
        "max_loc": max_loc,
        "max_kb": max_kb,
        "pragma_versions": pragma_versions,
        "file_records": file_records,
    }

def fmt_cell(entry, w_id, w_cnt, w_avg, w_med):
    if entry is None: return " " * (w_id + 2 + w_cnt + 2 + w_avg + 2 + w_med)
    repo_id, cnt, avg_loc, med_loc = entry
    return (
        f"{repo_id.ljust(w_id)}  "
        f"{str(cnt).ljust(w_cnt)}  "
        f"{str(avg_loc).ljust(w_avg)}  "
        f"{str(med_loc).ljust(w_med)}"
    )

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="out", help="Path to /out")
    p.add_argument("--contracts", default="web3bugs/contracts", help="Path to Web3Bugs contracts")
    p.add_argument("--extensions", action="append", help="File extensions counted (default: .sol, .vy)")
    p.add_argument("--tsv", action="store_true", help="TSV dump of per-repo stats")
    args = p.parse_args()

    out_dir = Path(args.out).resolve()
    contracts_root = Path(args.contracts).resolve()

    if not out_dir.exists(): raise SystemExit(f"Out not found: {out_dir}")
    if not contracts_root.exists(): raise SystemExit(f"Contracts not found: {contracts_root}")

    exts = [e.lower() if e.startswith(".") else ("." + e.lower()) for e in (args.extensions or [".sol", ".vy"])]
    per_repo_rows, missing = [], []
    all_contract_counts, all_file_locs, all_file_records, pragma_counter = [], [], [], Counter()
    grand_total_contracts, grand_total_loc = 0, 0
    filename_to_repos = defaultdict(set)
    heaviest_by_cnt = (None, 0)
    heaviest_by_loc = (None, 0)

    for repo_id in list_out(out_dir):
        repo_path = contracts_root / repo_id
        if not repo_path.exists():
            missing.append(repo_id)
            continue

        stats = scan_repo(repo_path, exts)
        cnt_files = stats["cnt_files"]
        avg_loc = stats["avg_loc"]
        med_loc = stats["med_loc"]
        total_loc = stats["total_loc"]

        per_repo_rows.append((repo_id, cnt_files, avg_loc, med_loc))
        all_contract_counts.append(cnt_files)
        grand_total_contracts += cnt_files
        grand_total_loc += total_loc

        for relp, loc_nonempty, size_bytes in stats["file_records"]:
            all_file_locs.append(loc_nonempty)
            all_file_records.append((repo_id, relp, loc_nonempty, size_bytes))
            base = os.path.basename(relp)
            filename_to_repos[base].add(repo_id)

        for pragma in stats["pragma_versions"]: pragma_counter[pragma] += 1

        if cnt_files > heaviest_by_cnt[1]: heaviest_by_cnt = (repo_id, cnt_files)
        if total_loc > heaviest_by_loc[1]: heaviest_by_loc = (repo_id, total_loc)

    total_repos = len(per_repo_rows)
    largest_file = None
    for repo_id, relp, loc_nonempty, size_bytes in all_file_records:
        size_kb = size_bytes // 1024
        if largest_file is None:
            largest_file = (repo_id, relp, size_kb, loc_nonempty)
        else:
            _, _, best_kb, best_loc = largest_file
            if size_kb > best_kb or (size_kb == best_kb and loc_nonempty > best_loc):
                largest_file = (repo_id, relp, size_kb, loc_nonempty)

    dup_filenames = sum(1 for _, repos in filename_to_repos.items() if len(repos) >= 2)
    mean_cnt = (sum(all_contract_counts) / total_repos) if total_repos else 0
    median_cnt = statistics.median(all_contract_counts) if all_contract_counts else 0
    p90_cnt = (
        statistics.quantiles(all_contract_counts, n=10)[8]
        if len(all_contract_counts) >= 2 else median_cnt
    )

    mean_loc_per_file = (sum(all_file_locs) / len(all_file_locs)) if all_file_locs else 0
    median_loc_per_file = statistics.median(all_file_locs) if all_file_locs else 0
    p90_loc_per_file = (
        statistics.quantiles(all_file_locs, n=10)[8]
        if len(all_file_locs) >= 2 else median_loc_per_file
    )

    per_repo_rows.sort(key=lambda t: int(t[0]))

    if args.tsv:
        for repo_id, cnt_files, avg_loc, med_loc in per_repo_rows: print(f"{repo_id}\t{cnt_files}\t{avg_loc}\t{med_loc}")
    else:
        w_id = max(max((len(rid) for rid, _, _, _ in per_repo_rows), default=2), len("ID"))
        w_cnt = max(max((len(str(c)) for _, c, _, _ in per_repo_rows), default=3), len("Cnt"))
        w_avg = max(max((len(str(a)) for _, _, a, _ in per_repo_rows), default=1), len("AvgLOC"))
        w_med = max(max((len(str(m)) for _, _, _, m in per_repo_rows), default=1), len("MedLOC"))

        col_h = math.ceil(len(per_repo_rows) / 3)
        col1 = per_repo_rows[:col_h]
        col2 = per_repo_rows[col_h:2 * col_h]
        col3 = per_repo_rows[2 * col_h:]

        gap = "    "

        hdr = (
            f"{'ID'.ljust(w_id)}  "
            f"{'Cnt'.ljust(w_cnt)}  "
            f"{'AvgLOC'.ljust(w_avg)}  "
            f"{'MedLOC'.ljust(w_med)}"
        )

        header_line = hdr
        if col2: header_line += gap + hdr
        if col3: header_line += gap + hdr
        print(header_line)

        underline_seg = (
            f"{'-' * w_id}  "
            f"{'-' * w_cnt}  "
            f"{'-' * w_avg}  "
            f"{'-' * w_med}"
        )

        underline_line = underline_seg
        if col2: underline_line += gap + underline_seg
        if col3: underline_line += gap + underline_seg
        print(underline_line)

        max_rows = max(len(col1), len(col2), len(col3))
        for r in range(max_rows):
            c1 = fmt_cell(col1[r] if r < len(col1) else None, w_id, w_cnt, w_avg, w_med)
            line = c1
            if col2:
                c2 = fmt_cell(col2[r] if r < len(col2) else None, w_id, w_cnt, w_avg, w_med)
                line += gap + c2
            if col3:
                c3 = fmt_cell(col3[r] if r < len(col3) else None, w_id, w_cnt, w_avg, w_med)
                line += gap + c3
            print(line)

    print(f"[TOTAL] Repos: {total_repos}\t\tContracts: {grand_total_contracts}\t\tNon-empty LOC: {grand_total_loc}")
    print(f"[MEAN Contracts/Repo]: {mean_cnt:.2f}\t[MEDIAN Contracts/Repo]: {int(median_cnt)}\t[P90 Contracts/Repo]: {int(round(p90_cnt))}")
    print(f"[MEAN LOC/File]: {mean_loc_per_file:.2f}\t\t[MEDIAN LOC/File]: {int(median_loc_per_file)}\t\t[P90 LOC/File]: {int(round(p90_loc_per_file))}")

    if heaviest_by_cnt[0] is not None:
        print(f"[HEAVIEST] ID By Contracts: {heaviest_by_cnt[0]} -> {heaviest_by_cnt[1]} files", end="\t")
    if heaviest_by_loc[0] is not None:
        print(f"ID By LOC: {heaviest_by_loc[0]} -> {heaviest_by_loc[1]} LOC")
    if largest_file is not None:
        lf_repo, lf_rel, lf_kb, lf_loc = largest_file
        print(f"[LARGEST Single File]: {lf_repo}/{lf_rel} -> {lf_kb} KB, {lf_loc} LOC")

    print(f"[CROSS-REPO DUPLICATE FILENAMES >=2 REPOS]: {dup_filenames}")

    if pragma_counter:
        print("[SOLIDITY VERSION HISTOGRAM]:")
        tabs = 0
        for pragma, count in sorted(pragma_counter.items(), key=lambda x: (-x[1], x[0])):
            prg = pragma.replace("pragma solidity ", "")
            if tabs == 4:
                tabs = 0
                print()
            result = f"{prg}: {count} repos"
            print(result, end=((30 - len(result)) * " "))
            tabs += 1
    if missing: print("Skipped (present in --out but missing under --contracts): " + ", ".join(missing))

if __name__ == "__main__": main()
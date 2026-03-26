#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

def derive_label_from_path(p):
    try:
        parts = p.parts
        return parts[parts.index("out")+1]
    except Exception:
        return p.parent.parent.name

def assess_failure(meta, meta_err):
    reasons = []
    if meta is None:
        reasons.append("meta.json missing/invalid" + (f" ({meta_err})" if meta_err else ""))
        return True, reasons

    rc, ok = meta.get("rc"), meta.get("ok")
    status = (meta.get("status_line") or "").strip()
    has_findings = bool(meta.get("is_json_present"))

    if ok is False: reasons.append("ok=false")
    if isinstance(rc, int) and rc != 0: reasons.append(f"rc={rc}")
    if status.upper().startswith("ERR"): reasons.append("status=ERR")
    if not has_findings: reasons.append("findings.json missing")
    return (len(reasons)>0), reasons

def load_meta(p):
    try: return json.loads(p.read_text(encoding="utf-8")), None
    except Exception as e: return None, str(e)

def sort_key(r):
    label, abl_id, name, *_ = r
    try: n = int(abl_id) if abl_id is not None else int(name.split(":")[0].split("-")[0])
    except Exception: n = 10**9
    return (label.lower(), n, str(name))

def main():
    ap = argparse.ArgumentParser(description="Get failed SI detector runs from ./out")
    ap.add_argument("--out-dir", default="out", help="Path to /out")
    ap.add_argument("--all", action="store_true", help="Print ALL runs including S/F/?")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of TSV")
    args = ap.parse_args()

    out_root = Path(args.out_dir).resolve()
    if not out_root.exists():
        print(f"[FATAL] out directory not found: {out_root}", file=sys.stderr)
        return 2

    rows = []
    for meta_path in out_root.rglob("meta.json"):
        meta, meta_err = load_meta(meta_path)
        failed, reasons = assess_failure(meta, meta_err)

        # Derive the label or ablation if present
        label = (meta or {}).get("label") or derive_label_from_path(meta_path)
        abl_id = (meta or {}).get("ablation_id")
        name = (meta or {}).get("name") or str(meta_path.parent.name)
        rc, ok, status = (meta or {}).get("rc"), (meta or {}).get("ok"), (meta or {}).get("status_line") or ""
        rows.append((label, abl_id, name, rc, ok, status, str(meta_path.parent), failed, reasons))

    # Flag directories that should have a meta.json but don’t
    for label_dir in out_root.iterdir():
        if not label_dir.is_dir(): continue
        for run_dir in label_dir.iterdir():
            if not run_dir.is_dir(): continue
            meta_path = run_dir / "meta.json"
            if not meta_path.exists():
                label, abl_name = label_dir.name, run_dir.name
                failed, reasons = True, ["meta.json missing"]
                rows.append((label, None, abl_name, None, None, "", str(run_dir), failed, reasons))

    # Sort by label then ablation id or name
    rows.sort(key=sort_key)

    failures = [r for r in rows if r[8]]
    if args.json:
        payload = []
        for (label, abl_id, name, rc, ok, status, path, failed, reasons) in (rows if args.all else failures):
            payload.append({
                "label": label,
                "ablation_id": abl_id,
                "name": name,
                "rc": rc,
                "ok": ok,
                "status": status,
                "run_dir": path,
                "failed": failed,
                "reasons": reasons,
            })
        print(json.dumps(payload, indent=2))
    else:
        print("label\tablation_id\tname\trc\tok\tstatus\trun_dir\tfailed\treasons")
        for (label, abl_id, name, rc, ok, status, path, failed, reasons) in (rows if args.all else failures):
            print(f"{label}\t{abl_id}\t{name}\t{rc}\t{ok}\t{status}\t{path}\t{failed}\t{','.join(reasons)}")

    total, nfail = len(rows), len(failures)
    print(f"[SUMMARY] scanned={total} runs, failures={nfail}", file=sys.stderr)
    return 1 if nfail > 0 else 0

if __name__ == "__main__": sys.exit(main())
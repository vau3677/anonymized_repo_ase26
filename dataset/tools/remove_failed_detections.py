import re
from pathlib import Path
tsv_path = Path(__file__).resolve().parent.parent / "out" / "done.tsv"
pattern = re.compile(r"\b\d+c/1/\d+r\b")
def main():
    if not tsv_path.exists(): raise FileNotFoundError(f"File not found: {tsv_path}")
    lines = tsv_path.read_text().splitlines()
    kept = [line for line in lines if pattern.search(line)]
    tsv_path.write_text("\n".join(kept) + ("\n" if kept else ""))
    print(f"Filtered {len(lines) - len(kept)} invalid lines.\nKept {len(kept)} valid lines in {tsv_path}.")
if __name__ == "__main__": main()
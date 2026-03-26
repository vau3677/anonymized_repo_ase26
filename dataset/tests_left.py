import os
contracts_root, out_root = "Web3Bugs/contracts", "out"
def numeric_dirs(root): return { name for name in os.listdir(root) if os.path.isdir(os.path.join(root, name)) and name.isdigit() }
contracts_folders = numeric_dirs(contracts_root)
out_folders = numeric_dirs(out_root)
missing_in_out = contracts_folders - out_folders
print(f"Numeric contract folders: {len(contracts_folders)}")
print(f"Numeric out folders: {len(out_folders)}")
print(f"Missing numeric folders ({len(missing_in_out)}):")
for folder in sorted(missing_in_out): print(folder, end=' ')

import json

nb_path = 'c:\\Users\\lenovo\\Desktop\\DASK_NEW\\building_analysis_simple.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# Find and fix the brace_xz cell
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "BRACES XZ" in source and "is_face and is_center_bay" in source:
            # Replace the old logic with new logic
            new_source = source.replace(
                "# On Faces: Skip Center Bay (Chevron is there)\n            if is_face and is_center_bay:\n                continue",
                "# Skip Center Bay entirely (Core wall + Chevron area)\n            if is_center_bay:\n                continue"
            )
            cell['source'] = [new_source]
            print(f"Fixed brace_xz center bay skip logic in cell {i}")
            break

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Notebook updated.")

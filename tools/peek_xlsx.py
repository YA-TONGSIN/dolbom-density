import sys, openpyxl

path = sys.argv[1]
wb = openpyxl.load_workbook(path, read_only=True, data_only=True)

for name in wb.sheetnames:
    ws = wb[name]
    print("=" * 78)
    print(f"[{name}]  rows={ws.max_row}  cols={ws.max_column}")
    rows = ws.iter_rows(min_row=1, max_row=4, values_only=True)
    for i, r in enumerate(rows):
        label = "헤더" if i == 0 else f"행{i}"
        cells = ["" if v is None else str(v) for v in r]
        print(f"  {label}: " + " | ".join(cells[:20]))
    print()

wb.close()

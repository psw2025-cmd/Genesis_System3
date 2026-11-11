import openpyxl

files = [
    'PHASE3_TEST_RESULTS.xlsx',
    'PHASE4_CLOUD_VERIFICATION.xlsx',
    'DEPLOYMENT_SIGNOFF.xlsx',
    'GENESIS_FINAL_IMPLEMENTATION_REPORT.xlsx'
]

for f in files:
    wb = openpyxl.load_workbook(f, data_only=True)
    print(f"==================== {f} ====================")
    for s in wb.sheetnames:
        ws = wb[s]
        print(f"\n--- Sheet: {s} (rows={ws.max_row}, cols={ws.max_column}) ---")
        for row in ws.iter_rows(values_only=True):
            if any(row):
                print(row)

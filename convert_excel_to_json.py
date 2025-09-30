"""convert_excel_to_json.py
Run locally (not on Vercel). Converts Excel sheets into JSON files under data/.
Usage:
    python convert_excel_to_json.py "Result Analysis of B.Tech. IV Sem 2024-25.xlsx"
"""

import os, sys, json, pandas as pd
EXPECTED_BRANCHES = ['CS', 'CSR-D', 'AI&DS-E', 'CS(AI)-F', 'CS(DS)-G', 'CS(IOT)-H']
SKIPROWS = 10  # adjust if needed

def sanitize_colnames(df):
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df

def main(excel_path):
    if not os.path.exists(excel_path):
        print("Excel file not found:", excel_path)
        return 1
    xls = pd.ExcelFile(excel_path)
    os.makedirs("data", exist_ok=True)
    for sheet in xls.sheet_names:
        if sheet not in EXPECTED_BRANCHES:
            continue
        print("Processing sheet:", sheet)
        df = pd.read_excel(excel_path, sheet_name=sheet, skiprows=SKIPROWS)
        df = sanitize_colnames(df)
        df = df.fillna("").astype(str)
        records = df.to_dict(orient="records")
        out_path = os.path.join("data", f"{sheet}.json")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(records, fh, ensure_ascii=False, indent=2)
        print("Wrote:", out_path)
    print("Done.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_excel_to_json.py <excel-file.xlsx>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))

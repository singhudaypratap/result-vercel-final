# Vercel deployment - Python serverless + static frontend

1. Convert Excel -> JSON locally:
   - create venv: `python3 -m venv venv && source venv/bin/activate`
   - `pip install pandas openpyxl`
   - `python convert_excel_to_json.py "Result Analysis of B.Tech. IV Sem 2024-25.xlsx"`
   - This creates `data/<branch>.json`. Add these files to your git repo.

2. Project layout:
   ```
   .
   ├─ api/
   │  └─ result.py
   ├─ data/
   │  ├─ CS.json
   │  └─ ...
   ├─ public/
   │  └─ index.html
   ├─ vercel.json
   └─ requirements.txt
   ```

3. Deploy:
   - Initialize a git repo, commit, and push to GitHub.
   - Import the repo on Vercel or use `vercel` CLI.
   - Vercel will run Python serverless functions under `api/`.

Notes:
- To update results, re-run conversion script locally, commit updated `data/*.json` and redeploy.
- If you prefer dynamic updates without redeploys, host JSON on S3 and update `api/result.py` to fetch from S3.

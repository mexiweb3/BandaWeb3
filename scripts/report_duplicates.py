
import json
import zipfile
import re
from datetime import datetime
import sys
import os
sys.path.append(os.getcwd())
import scripts.manual_xlsx_parse as parser

# --- Helpers ---
def normalize_title(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())

def extract_date(date_str):
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

# --- Main ---
file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

# 1. Load Excel
excel_eps = []
try:
    with zipfile.ZipFile(file_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        for row in raw_rows:
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            if not desc_cell or not desc_cell.get('value') or 'Ended:' not in desc_cell['value']: continue

            desc_raw = desc_cell['value']
            parts = desc_raw.split(' - Ended: ')
            title = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            date_part = rest.split(' - ')[0] if ' - ' in rest else rest
            date_str = extract_date(date_part)
            
            if date_str:
                excel_eps.append({'title': title, 'date': date_str})
except Exception:
    pass

# 2. Load DB
with open(db_path, 'r') as f:
    db = json.load(f)

db_titles = set()
db_dates = {}
for ep in db['episodes']:
    t = normalize_title(ep.get('title', ''))
    if t: db_titles.add(t)
    d = ep.get('date')
    if d:
        if d not in db_dates: db_dates[d] = []
        db_dates[d].append(ep)

# 3. Compare
print(f"| Fecha | Título en Excel | Título(s) en BD | Notas |")
print(f"|---|---|---|---|")

for cand in excel_eps:
    norm_title = normalize_title(cand['title'])
    if norm_title in db_titles: continue
    
    match_on_date = db_dates.get(cand['date'])
    if match_on_date:
        db_titles_str = "<br>".join([f"- {e.get('title')}" for e in match_on_date])
        print(f"| {cand['date']} | {cand['title']} | {db_titles_str} | Posiblemente diferente (misma fecha) |")

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
    # Format: Nov 3 2025
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

# --- Main ---
file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

print("Loading data...")

# 1. Load Excel Candidates
excel_eps = []
try:
    with zipfile.ZipFile(file_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        for row in raw_rows:
            # Find description cell (Col B) and other cols
            title = ""
            date_str = None
            
            # Row is list of dicts: {'ref': 'A1', 'value':...}
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            
            if not desc_cell or not desc_cell.get('value') or 'Ended:' not in desc_cell['value']:
                continue

            desc_raw = desc_cell['value']
            parts = desc_raw.split(' - Ended: ')
            title = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            date_part = rest.split(' - ')[0] if ' - ' in rest else rest
            date_str = extract_date(date_part)
            
            if date_str:
                excel_eps.append({
                    'title': title,
                    'date': date_str,
                    'orig_row': row # Keep raw row list
                })

except Exception as e:
    print(f"Error parsing Excel: {e}")
    exit(1)

# 2. Load DB
with open(db_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

# Build lookups
db_titles = set()
db_dates = {} # Map date -> list of episodes
for ep in db['episodes']:
    t = normalize_title(ep.get('title', ''))
    if t: db_titles.add(t)
    
    d = ep.get('date')
    if d:
        if d not in db_dates:
            db_dates[d] = []
        db_dates[d].append(ep)

# 3. Analyze Candidates
truly_new = []
potential_dupes = []

print(f"\nAnalyzing {len(excel_eps)} episodes from Excel against {len(db['episodes'])} in DB...")

for cand in excel_eps:
    norm_title = normalize_title(cand['title'])
    
    # Exact title match already handled/ignored?
    if norm_title in db_titles:
        continue
        
    # Check date match
    match_on_date = db_dates.get(cand['date'])
    
    if match_on_date:
        # Found existing episodes on this date
        potential_dupes.append({
            'candidate': cand,
            'existing': match_on_date
        })
    else:
        # No title match AND no date match -> Truly New
        truly_new.append(cand)

# 4. Report
print(f"\n=== RESULTADOS ===")
print(f"Total en Excel: {len(excel_eps)}")
print(f"Ya en DB (Title Match): {len(excel_eps) - len(truly_new) - len(potential_dupes)}")
print(f"Posibles Duplicados (Misa Fecha, Diferente Titulo): {len(potential_dupes)}")
print(f"Definitivamente Nuevos (Fecha Única): {len(truly_new)}")

if len(potential_dupes) > 0:
    print("\n--- POSIBLES DUPLICADOS (Revisar Manualmente) ---")
    for item in potential_dupes[:20]: # Show first 20
        c = item['candidate']
        print(f"\n[Excel] {c['date']}: {c['title']}")
        for e in item['existing']:
            print(f"  -> [DB] {e.get('title')} (Type: {e.get('type')})")

if len(truly_new) > 0:
    print("\n--- DEFINITIVAMENTE NUEVOS (Ejemplos) ---")
    for c in truly_new[:10]:
        print(f"[NEW] {c['date']}: {c['title']}")

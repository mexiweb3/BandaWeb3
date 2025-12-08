import json
import zipfile
import re
from datetime import datetime
import sys
import os
sys.path.append(os.getcwd())
import scripts.manual_xlsx_parse as parser
import scripts.sync_cohosted_excel as sync_logic

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
file_path = 'shared/inputs/Hosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

print("Starting Hosted Episodes Sync...")

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
            desc_link = desc_cell.get('link')
            parts = desc_raw.split(' - Ended: ')
            title = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            date_part = rest.split(' - ')[0] if ' - ' in rest else rest
            date_str = extract_date(date_part)
            
            # Duration
            duration_match = re.search(r'Duration: (.*?)$', desc_raw)
            duration = duration_match.group(1).strip() if duration_match else ""
            
            # Link (Col D)
            link_cell = next((c for c in row if c['ref'].startswith('D')), None)
            space_url = link_cell.get('link') if link_cell else ""
            
            # Listeners (Col C)
            list_cell = next((c for c in row if c['ref'].startswith('C')), None)
            try: listeners = int(float(list_cell['value'])) if list_cell else 0
            except: listeners = 0
            
            if date_str:
                excel_eps.append({
                    'title': title,
                    'date': date_str,
                    'duration': duration,
                    'space_url': space_url,
                    'spacesdashboard_url': desc_link or "",
                    'listeners': listeners,
                    'raw_title': title
                })

except Exception as e:
    print(f"Error parsing Excel: {e}")
    exit(1)

print(f"Loaded {len(excel_eps)} episodes from Excel.")

# 2. Load DB
with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build a map of potential DB matches
# Since we need to match multiple entries per day (sometimes), we need a flexible matching strategy.
# Strategy:
# 1. Group DB episodes by (title_norm, date).
# 2. Consume matches as we blindly proceed?
#    - If we have 2 excel eps for same day/title, and 1 DB ep:
#      - Match first excel to DB (update).
#      - Second excel finds no "unused" DB match -> Create new.
#    - If we have 2 excel eps and 2 DB eps:
#      - Match first to first.
#      - Match second to second.

# --- Improved Matching Logic v5 ---
# Group DB key indices
db_by_date = {}
db_by_number = {}

for ep in data['episodes']:
    # Index by Date
    d = ep.get('date')
    if d:
        if d not in db_by_date: db_by_date[d] = []
        db_by_date[d].append(ep)
        
    # Index by Number (as INTEGER for robust matching)
    t = ep.get('title', '')
    num_match = re.search(r'#(\d+)', t)
    
    # Try title first
    if num_match:
        try:
            num = int(num_match.group(1))
            if num not in db_by_number: db_by_number[num] = []
            db_by_number[num].append(ep)
        except: pass
    
    # Try number field
    # Be careful, sometimes number field is date string (e.g. 20250101)
    # We only want sequence numbers (e.g. 1 to 999)
    if ep.get('number'):
        try:
            n_val = int(str(ep['number']))
            if 0 < n_val < 1000: # Heuristic: Sequence numbers are usually small
                if n_val not in db_by_number: db_by_number[n_val] = []
                # Avoid duping if already added by title
                if ep not in db_by_number[n_val]: 
                    db_by_number[n_val].append(ep)
        except: pass

updated_count = 0
added_count = 0

for i, excel_ep in enumerate(excel_eps):
    excel_date = excel_ep['date']
    excel_title = excel_ep['raw_title']
    excel_title_norm = normalize_title(excel_title)
    
    # Extract episode number from Excel title
    excel_num_match = re.search(r'#(\d+)', excel_title)
    excel_num_int = int(excel_num_match.group(1)) if excel_num_match else None

    # --- Manual Corrections ---
    # User feedback: #064 in Excel (@byluaambriz) is actually #063
    # Check title/date identifying features
    if 'byluaambriz' in excel_title_norm and excel_num_int == 64:
        print("Handling Manual Correction: @byluaambriz #064 -> #063")
        excel_num_int = 63
    # --------------------------

    match = None
    
    # Priority 1: Global Number Match (Strongest)
    if excel_num_int is not None and excel_num_int in db_by_number:
        cands = db_by_number[excel_num_int]
        if len(cands) == 1:
            match = cands[0]
        else:
            # Multiple matches with same number? Pick best date match
            for c in cands:
                if c.get('date') == excel_date:
                    match = c
                    break
            if not match: match = cands[0]
            
    # Priority 2: Date + Title Match
    if not match:
        candidates = db_by_date.get(excel_date, [])
        if candidates:
            for cand in candidates:
                cand_title_norm = normalize_title(cand.get('title', ''))
                # Exact or containment
                if cand_title_norm == excel_title_norm:
                     match = cand
                     break
                elif cand_title_norm in excel_title_norm or excel_title_norm in cand_title_norm:
                     match = cand
                     break
    
    if match:
        # Update existing
        match['space_url'] = excel_ep['space_url']
        if excel_ep['spacesdashboard_url']:
            match['spacesdashboard_url'] = excel_ep['spacesdashboard_url']
            
        if match.get('analytics_source') != 'X Spaces Analytics':
            match['listeners'] = excel_ep['listeners']
            match['analytics_source'] = 'spaces_dashboard_excel'
            if not match.get('duration') and excel_ep['duration']:
                match['duration'] = excel_ep['duration']
            elif excel_ep['duration']:
                 pass

        updated_count += 1
    else:
        # Create NEW
        new_ep = {
            "title": excel_ep['raw_title'],
            "date": excel_ep['date'],
            "number": excel_ep['date'].replace('-', ''),
            "type": "hosted",
            "is_numbered": False,
            "host": "BandaWeb3",
            "description": f"Hosted Space: {excel_ep['raw_title']}",
            "guests": [],
            "topics": [],
            "status": "archived",
            "transcript_available": False,
            "content_generated": False,
            "flyer_urls": [],
            "duration": excel_ep['duration'],
            "space_url": excel_ep['space_url'],
            "spacesdashboard_url": excel_ep['spacesdashboard_url'],
            "listeners": excel_ep['listeners'],
            "analytics_source": 'spaces_dashboard_excel'
        }
        data['episodes'].append(new_ep)
        added_count += 1
        print(f"Added NEW: {excel_ep['date']} - {excel_ep['raw_title']}")

data['episodes'].sort(key=lambda x: x.get('date', ''), reverse=True)

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Sync Complete.\nUpdated: {updated_count}\nAdded: {added_count}")

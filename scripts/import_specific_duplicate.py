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
file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'
target_title = "Ciudad Gitcoin 🚀"
target_date = "2023-08-23"

print(f"Force importing duplicates for: {target_title} ({target_date})")

# 1. Load Excel Candidates
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
            
            if title == target_title and date_str == target_date:
                # Duration
                duration_match = re.search(r'Duration: (.*?)$', desc_raw)
                duration = duration_match.group(1).strip() if duration_match else ""
                
                # Host
                host_cell = next((c for c in row if c['ref'].startswith('A')), None)
                host_raw = host_cell['value'] if host_cell else ""
                host_link = host_cell.get('link') if host_cell else ""
                host = sync_logic.extract_handle(host_raw, host_link)

                # Link
                link_cell = next((c for c in row if c['ref'].startswith('D')), None)
                space_url = link_cell.get('link') if link_cell else ""
                
                # Listeners
                list_cell = next((c for c in row if c['ref'].startswith('C')), None)
                try: listeners = int(float(list_cell['value'])) if list_cell else 0
                except: listeners = 0

                excel_eps.append({
                    'title': title,
                    'date': date_str,
                    'duration': duration,
                    'host': host,
                    'space_url': space_url,
                    'spacesdashboard_url': desc_link or "",
                    'listeners': listeners,
                    'description': f"Co-hosted Space: {title}. Host: {host}",
                    'guests': [],
                    'topics': [],
                    'status': 'archived',
                    'transcript_available': False,
                    'content_generated': False,
                    'flyer_urls': [],
                    'type': 'co-hosted',
                    'analytics_source': 'spaces_dashboard_excel'
                })

except Exception as e:
    print(f"Error parsing Excel: {e}")
    exit(1)

print(f"Found {len(excel_eps)} matching rows in Excel.")

# 2. Load DB
with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count existing in DB
db_count = 0
for ep in data['episodes']:
    if ep.get('title') == target_title and ep.get('date') == target_date:
        db_count += 1

print(f"Found {db_count} matching episodes in DB.")

# 3. Add Missing
needed = len(excel_eps) - db_count

if needed > 0:
    print(f"Adding {needed} duplicate(s)...")
    for i in range(needed):
        # Taking the (db_count + i)-th from excel list to try and match order if they differ? 
        # Actually they are likely identical metadata-wise unless one has diff listeners.
        # Let's verify if excel_eps differ.
        
        # Simple strategy: Add the next one from excel list logic-wise
        # Just append a copy of the excel data.
        ep_to_add = excel_eps[db_count + i].copy() # Use the specific index corresponding to the missing one
        ep_to_add['number'] = ep_to_add['date'].replace('-', '')
        data['episodes'].append(ep_to_add)
        print(f"Added clone: {ep_to_add['title']}")

    # Sort
    data['episodes'].sort(key=lambda x: x.get('date', ''), reverse=True)

    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
else:
    print("Database already has enough copies.")

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
    # Improved normalization: if strictly alphanumeric is empty (emojis), keep original
    norm = re.sub(r'[^a-z0-9]', '', t.lower())
    return norm if norm else t.strip()

def extract_date(date_str):
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

# --- Main ---
file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

print("Loading data for remaining import...")

# 1. Load Excel Candidates
excel_eps = []
try:
    with zipfile.ZipFile(file_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        for row in raw_rows:
            # Find description cell (Col B)
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            
            if not desc_cell or not desc_cell.get('value') or 'Ended:' not in desc_cell['value']:
                continue

            desc_raw = desc_cell['value']
            # Extract links if any
            desc_link = desc_cell.get('link')

            # Parse description
            parts = desc_raw.split(' - Ended: ')
            title = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            date_part = rest.split(' - ')[0] if ' - ' in rest else rest
            date_str = extract_date(date_part)
            
            # Duration
            duration_match = re.search(r'Duration: (.*?)$', desc_raw)
            duration = duration_match.group(1).strip() if duration_match else ""

            # Host (Col A)
            host_cell = next((c for c in row if c['ref'].startswith('A')), None)
            host_raw = host_cell['value'] if host_cell else ""
            host_link = host_cell.get('link') if host_cell else ""
            host = sync_logic.extract_handle(host_raw, host_link)

            # Link (Col D)
            link_cell = next((c for c in row if c['ref'].startswith('D')), None)
            space_url = link_cell.get('link') if link_cell else ""
            
            # Listeners (Col C)
            list_cell = next((c for c in row if c['ref'].startswith('C')), None)
            listeners_str = list_cell['value'] if list_cell else "0"
            try:
                listeners = int(float(listeners_str))
            except ValueError:
                listeners = 0

            if date_str:
                excel_eps.append({
                    'title': title, # Keep original title for insertion
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

# 2. Load DB
with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

db_titles = set()
for ep in data['episodes']:
    t = normalize_title(ep.get('title', ''))
    if t: db_titles.add(t)

# 3. Filter New (Only check Title uniqueness)
to_add = []
for ep in excel_eps:
    norm_title = normalize_title(ep['title'])
    
    # Check title match
    if norm_title in db_titles:
        continue
    
    # Intentionally ignoring date check as per user request
    to_add.append(ep)

print(f"Found {len(to_add)} remaining episodes to add.")

# 4. Add to DB
if to_add:
    for ep in to_add:
        # Use date as number placeholder
        ep['number'] = ep['date'].replace('-', '')
        data['episodes'].append(ep)
        print(f"Adding: {ep['date']} - {ep['title']}")
    
    # Sort
    data['episodes'].sort(key=lambda x: x.get('date', ''), reverse=True)
    
    # Save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nSuccessfully added {len(to_add)} episodes!")
else:
    print("No new episodes found to add.")

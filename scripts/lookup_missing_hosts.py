import json
import zipfile
import re
from datetime import datetime
import sys
import os
sys.path.append(os.getcwd())
import scripts.manual_xlsx_parse as parser

def normalize_title(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())

def extract_date(date_str):
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

# Files
excel_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

# Load DB
with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Identify missing host episodes
targets = []
for ep in data['episodes']:
    if ep.get('type') == 'co-hosted' and not ep.get('host'):
        targets.append(ep)

print(f"Found {len(targets)} co-hosted episodes missing host.")
if not targets:
    exit(0)

# Create lookup map from Excel
# We need (Date, Title) -> Host
lookup_map = {} # Key: Date (since titles might vary slightly, but dates are usually good for SpacesDashboard exports)

try:
    with zipfile.ZipFile(excel_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        for row in raw_rows:
            # Col A: Host (The one we want)
            host_cell = next((c for c in row if c['ref'].startswith('A')), None)
            host_raw = host_cell['value'] if host_cell else "Unknown"
            
            # Extract handle from Host field (e.g. "Name@handle")
            # Usually format is "Name@handle" or just "Name". 
            # If we can extract @handle, perfect.
            host_clean = host_raw
            if '@' in host_raw:
                # heuristic: splitting by @ and taking the last part often works for SpacesDashboard format "Name@handle"
                # But sometimes it's "Name @handle".
                parts = host_raw.split('@')
                if len(parts) > 1:
                    handle = parts[-1].split(' ')[0] # take immediate user
                    host_clean = f"@{handle}"
            
            # Col B: Description/Date
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            if not desc_cell or not desc_cell.get('value') or 'Ended:' not in desc_cell['value']: continue
            
            try:
                desc_raw = desc_cell['value']
                parts = desc_raw.split(' - Ended: ')
                if len(parts) < 2:
                    continue
                    
                rest = parts[1]
                date_part = rest.split(' - ')[0]
                date_str = extract_date(date_part)
                
                if date_str:
                    title = parts[0].strip()
                    if date_str not in lookup_map:
                        lookup_map[date_str] = []
                    lookup_map[date_str].append({
                        'title': title,
                        'host': host_clean,
                        'orig_row_host': host_raw
                    })
            except Exception as e:
                # print(f"Skipping row due to error: {e}")
                continue
                
except Exception as e:
    print(f"Error reading Excel: {e}")
    exit(1)

# Match and Update
updated_count = 0
for ep in targets:
    d = ep.get('date')
    ep_title_norm = normalize_title(ep.get('title', ''))
    
    candidates = lookup_map.get(d, [])
    
    best_match = None
    if len(candidates) == 1:
        best_match = candidates[0]
    elif len(candidates) > 1:
        # Fuzzy match title
        for cand in candidates:
            cand_norm = normalize_title(cand['title'])
            if cand_norm in ep_title_norm or ep_title_norm in cand_norm:
                best_match = cand
                break
    
    if best_match:
        ep['host'] = best_match['host']
        updated_count += 1
        print(f"Updated host for '{ep['title']}': {best_match['host']} (from {d})")
    else:
        print(f"Could not find match for: [{d}] {ep['title']}")

# Save
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Update Complete. {updated_count} episodes updated.")

import json
import zipfile
import re
from datetime import datetime
import sys
import os
sys.path.append(os.getcwd())
import scripts.manual_xlsx_parse as parser
import scripts.sync_cohosted_excel as sync_logic

def extract_date(date_str):
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

print("Importing skipped Row 60...")

try:
    with zipfile.ZipFile(file_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        # Row 60 is index 59 (0-based)
        if len(raw_rows) > 59:
            row = raw_rows[59]
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            desc_raw = desc_cell['value']
            
            # Custom parsing for this messy row
            # "THREADS vs Twitter...📈Ended: Jul 6 2023..."
            parts = desc_raw.split('Ended: ')
            title_part = parts[0]
            # Remove trailing emoji/garbage if needed, or keep it
            title = title_part.replace('📈', '').strip() # Clean slightly
            
            rest = parts[1]
            date_part = rest.split(' - ')[0]
            date_str = extract_date(date_part)
            
            print(f"Parsed: {date_str} - {title}")
            
            if date_str:
                # Host
                host_cell = next((c for c in row if c['ref'].startswith('A')), None)
                host_raw = host_cell['value'] if host_cell else ""
                host_link = host_cell.get('link') if host_cell else ""
                host = sync_logic.extract_handle(host_raw, host_link)
                
                ep = {
                    'title': title,
                    'date': date_str,
                    'duration': "2h 04m", # Hardcoded from inspection or parse
                    'host': host,
                    'space_url': "", # Link was likely lost or not in logic, check D col
                    'spacesdashboard_url': desc_cell.get('link', ''),
                    'listeners': 0, # Check C
                    'description': f"Co-hosted Space: {title}. Host: {host}",
                    'guests': [],
                    'topics': [],
                    'status': 'archived',
                    'transcript_available': False,
                    'content_generated': False,
                    'flyer_urls': [],
                    'type': 'co-hosted',
                    'analytics_source': 'spaces_dashboard_excel',
                    'number': date_str.replace('-', '')
                }
                
                # Link
                link_cell = next((c for c in row if c['ref'].startswith('D')), None)
                if link_cell: ep['space_url'] = link_cell.get('link', '')
                
                # Listeners
                list_cell = next((c for c in row if c['ref'].startswith('C')), None)
                if list_cell: 
                    try: ep['listeners'] = int(float(list_cell['value']))
                    except: pass
                
                # Add to DB
                with open(db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                data['episodes'].append(ep)
                data['episodes'].sort(key=lambda x: x.get('date', ''), reverse=True)
                
                with open(db_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
                print("Successfully added Row 60 episode.")
            else:
                print("Failed to parse date from Row 60 even with custom logic.")

except Exception as e:
    print(f"Error: {e}")

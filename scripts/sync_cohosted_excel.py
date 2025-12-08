import zipfile
import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime

file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

# --- XLSX Parsing Logic (Manual) ---

def parse_shared_strings(zf):
    strings = []
    try:
        with zf.open('xl/sharedStrings.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in root.findall('main:si', ns):
                text = ""
                t = si.find('main:t', ns)
                if t is not None:
                    text += t.text or ""
                for r in si.findall('main:r', ns):
                    t = r.find('main:t', ns)
                    if t is not None:
                        text += t.text or ""
                strings.append(text)
    except KeyError:
        pass
    return strings

def parse_hyperlinks(zf):
    links = {}
    try:
        with zf.open('xl/worksheets/_rels/sheet1.xml.rels') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            for rel in root.findall('rel:Relationship', ns):
                if rel.attrib.get('Type').endswith('/hyperlink'):
                    links[rel.attrib.get('Id')] = rel.attrib.get('Target')
    except KeyError:
        pass
    return links

def parse_sheet(zf, strings, links_map):
    rows = []
    with zf.open('xl/worksheets/sheet1.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        cell_hyperlinks = {}
        hyperlinks_tag = root.find('main:hyperlinks', ns)
        if hyperlinks_tag is not None:
            for hl in hyperlinks_tag.findall('main:hyperlink', ns):
                ref = hl.attrib.get('ref')
                rId = hl.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                if rId in links_map:
                    cell_hyperlinks[ref] = links_map[rId]

        sheet_data = root.find('main:sheetData', ns)
        for row in sheet_data.findall('main:row', ns):
            row_dict = {}
            for c in row.findall('main:c', ns):
                ref = c.attrib.get('r')
                col_letter = "".join(filter(str.isalpha, ref))
                t = c.attrib.get('t')
                v = c.find('main:v', ns)
                val = ""
                if v is not None:
                    if t == 's':
                        val = strings[int(v.text)]
                    else:
                        val = v.text
                
                link = cell_hyperlinks.get(ref)
                
                # Map columns to keys
                # A=Host, B=Description, C=Listeners, D=Link, E=Cohost
                key = None
                if col_letter == 'A': key = 'host_raw'
                elif col_letter == 'B': key = 'description_raw'
                elif col_letter == 'C': key = 'listeners'
                elif col_letter == 'D': key = 'space_url_raw'
                elif col_letter == 'E': key = 'cohost_raw'
                
                if key:
                    row_dict[key] = val
                    if key == 'space_url_raw' and link:
                        row_dict['space_url_link'] = link
                    if key == 'host_raw' and link:
                        row_dict['host_link'] = link
                    if key == 'description_raw' and link:
                        row_dict['description_link'] = link

            if row_dict:
                rows.append(row_dict)
    return rows

# --- Main Sync Logic ---

def normalize_title(t):
    return re.sub(r'[^a-z0-9]', '', t.lower())

def extract_date(date_str):
    # Format: Nov 3 2025
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

def extract_handle(raw_host, link):
    # Try to extract handle from raw text "Name@handle123k" -> @handle
    # Or from link "spacesdashboard.com/u/handle"
    if link and '/u/' in link:
        handle = link.split('/u/')[-1]
        return f"@{handle}"
    
    # Fallback to regex on raw text
    match = re.search(r'@(\w+)', raw_host)
    if match:
        return f"@{match.group(1)}"
    return raw_host

def sync():
    # 1. Parse Excel
    excel_rows = []
    with zipfile.ZipFile(file_path, 'r') as zf:
        strings = parse_shared_strings(zf)
        links_map = parse_hyperlinks(zf)
        raw_rows = parse_sheet(zf, strings, links_map)
        
        # Skip header rows (first 2 rows usually) and empty rows
        for r in raw_rows:
            if not r.get('description_raw'):
                continue
            if 'Ended:' not in r['description_raw']:
                continue
                
            desc_raw = r['description_raw']
            
            # Split Description: "Title - Ended: Date - Speakers: N - Duration: ..."
            parts = desc_raw.split(' - Ended: ')
            title = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            
            date_part = rest.split(' - ')[0] if ' - ' in rest else rest
            date_str = extract_date(date_part)
            
            duration_match = re.search(r'Duration: (.*?)$', desc_raw)
            duration = duration_match.group(1).strip() if duration_match else ""
            
            listeners = r.get('listeners', '0')
            try:
                listeners = int(float(listeners))
            except ValueError:
                listeners = 0
            
            space_url = r.get('space_url_link') or ""
            
            host = extract_handle(r.get('host_raw', ''), r.get('host_link', ''))
            
            spacesdashboard_url = r.get('description_link') or ""
            
            excel_rows.append({
                'title': title,
                'date': date_str,
                'duration': duration,
                'listeners': listeners,
                'space_url': space_url,
                'spacesdashboard_url': spacesdashboard_url,
                'host': host
            })
            
    print(f"Parsed {len(excel_rows)} rows from Excel.")

    # 2. Load DB
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    episodes = data.get('episodes', [])
    updated_count = 0
    
    # create map for faster lookup
    ep_map = {}
    for ep in episodes:
        # Use normalized title as key
        # Also maybe date? 
        key = normalize_title(ep.get('title', ''))
        if key:
            if key not in ep_map:
                ep_map[key] = []
            ep_map[key].append(ep)

    # 3. Match and Update
    for row in excel_rows:
        key = normalize_title(row['title'])
        matches = ep_map.get(key)
        
        target_ep = None
        if matches:
            # If multiple matches, try to match date
            if len(matches) > 1 and row['date']:
                for m in matches:
                    if m.get('date') == row['date']:
                        target_ep = m
                        break
            if not target_ep:
                target_ep = matches[0]
        
        if target_ep:
            # Update fields
            target_ep['space_url'] = row['space_url']
            target_ep['listeners'] = row['listeners']
            target_ep['duration'] = row['duration']
            target_ep['analytics_source'] = 'spaces_dashboard_excel'
            if row['spacesdashboard_url']:
                target_ep['spacesdashboard_url'] = row['spacesdashboard_url']
            
            # Only update host if it's currently BandaWeb3 or empty?
            # Or if Excel has a better host (not meximalist matching default)
            # The prompt says "revisa... actualiza la info" so I'll trust the Excel
            if row['host'] and row['host'] != '@meximalist': 
                 # Only update host if it's NOT meximalist (since user said co-hosted list)
                 # Wait, usually Host in Excel A column is the Creator. 
                 # If Creator is NOT meximalist, then it is a co-hosted space initiated by someone else.
                 target_ep['host'] = row['host']
            
            # Ensure type is co-hosted if not already?
            if target_ep.get('type') != 'co-hosted':
                 # Maybe user wants us to correct types too?
                 # "listado de los episodios que type cohosted"
                 pass 

            updated_count += 1
            print(f"Updated: {target_ep['title']}")
        else:
            print(f"Skipped (No Match): {row['title']} ({row['date']})")
    
    # 4. Save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSuccessfully updated {updated_count} episodes.")

if __name__ == '__main__':
    sync()

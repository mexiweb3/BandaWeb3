import zipfile
import re
import sys
import os
from datetime import datetime
sys.path.append(os.getcwd())
import scripts.manual_xlsx_parse as parser

def extract_date(date_str):
    try:
        dt = datetime.strptime(date_str.strip(), '%b %d %Y')
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return None

file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'

print("Checking date parsing for all rows...")

try:
    with zipfile.ZipFile(file_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        for i, row in enumerate(raw_rows):
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            desc_text = desc_cell['value'] if desc_cell else None
            
            if not desc_text or 'Ended:' not in desc_text:
                continue
                
            parts = desc_text.split(' - Ended: ')
            title = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            date_part = rest.split(' - ')[0] if ' - ' in rest else rest
            date_str = extract_date(date_part)
            
            if not date_str:
                print(f"FAILED DATE PARSE (Row {i+1}):")
                print(f"Text: {desc_text}")
                print(f"Date Part extracted: '{date_part}'")
                print("-" * 20)

except Exception as e:
    print(e)

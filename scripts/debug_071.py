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

file_path = 'shared/inputs/Hosted - Spaces Dashboard.xlsx'
db_path = 'shared/episodes_database.json'

print("DEBUGGING #071 Match...")

# Load DB 071
with open(db_path, 'r') as f:
    data = json.load(f)

db_071 = next((e for e in data['episodes'] if '#071' in e.get('title', '')), None)
if db_071:
    print(f"DB Found: {db_071['title']}")
    print(f"DB Date: '{db_071.get('date')}'")
    print(f"DB Norm: '{normalize_title(db_071['title'])}'")
else:
    print("DB #071 NOT FOUND!")

# Load Excel 071
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
            
            if '#071' in title:
                rest = parts[1]
                date_part = rest.split(' - ')[0]
                date_str = extract_date(date_part)
                
                print(f"Excel Found: {title}")
                print(f"Excel Date: '{date_str}'")
                print(f"Excel Norm: '{normalize_title(title)}'")
                
                if db_071:
                     # Simulate Check
                     db_d = db_071.get('date')
                     if db_d == date_str:
                         print("DATES MATCH!")
                         
                     db_n = normalize_title(db_071['title'])
                     ex_n = normalize_title(title)
                     if db_n == ex_n:
                         print("NORM TITLES MATCH!")
                     else:
                         print(f"TITLES NO MATCH! '{db_n}' vs '{ex_n}'")

except Exception as e:
    print(e)

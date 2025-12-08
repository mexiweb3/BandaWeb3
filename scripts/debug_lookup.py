import zipfile
import sys
import os
sys.path.append(os.getcwd())
import scripts.manual_xlsx_parse as parser

excel_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'

print("Debugging Specific Dates...")
target_dates = ['2023-07-06', '2022-11-28']

try:
    with zipfile.ZipFile(excel_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        for i, row in enumerate(raw_rows):
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            if not desc_cell or not desc_cell.get('value'): continue
            
            val = desc_cell['value']
            # Just print rows that contain our target strings or dates
            if 'THREADS' in val or 'Danny' in val or 'Jul 6' in val or 'Nov 28' in val:
                print(f"Row {i+1}: {val}")
                # Print Host
                host_cell = next((c for c in row if c['ref'].startswith('A')), None)
                print(f"  Host: {host_cell['value'] if host_cell else 'None'}")
                
except Exception as e:
    print(e)

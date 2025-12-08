import zipfile
import sys
import os
sys.path.append(os.getcwd())
import scripts.manual_xlsx_parse as parser

file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'

print("Analyzing ALL rows to find the skipped one...")

try:
    with zipfile.ZipFile(file_path, 'r') as zf:
        strings = parser.parse_shared_strings(zf)
        links_map = parser.parse_hyperlinks(zf)
        raw_rows = parser.parse_sheet(zf, strings, links_map)
        
        valid_count = 0
        skipped_candidates = []
        
        for i, row in enumerate(raw_rows):
            # i is 0-indexed, so Row 1 (header) is 0.
            # Row 2 (first data) is 1.
            
            desc_cell = next((c for c in row if c['ref'].startswith('B')), None)
            desc_text = desc_cell['value'] if desc_cell else None
            
            if not desc_text:
                continue
                
            # Check our filter
            if 'Ended:' in desc_text:
                valid_count += 1
            else:
                # It has text but no "Ended:" - likely the missing one if it's not the header
                # Ignorar encabezado ("Description")
                if desc_text.strip().lower() == 'description':
                    continue
                    
                skipped_candidates.append({
                    'row_idx': i+1, # Excel 1-based index
                    'text': desc_text
                })

        print(f"Valid Rows (with 'Ended:'): {valid_count}")
        print(f"Skipped Rows (with text in Col B): {len(skipped_candidates)}")
        
        for s in skipped_candidates:
            print(f"- Row {s['row_idx']}: {s['text']}")

except Exception as e:
    print(e)

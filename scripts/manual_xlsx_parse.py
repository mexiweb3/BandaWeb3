import zipfile
import xml.etree.ElementTree as ET
import re

file_path = 'shared/inputs/Cohosted - Spaces Dashboard.xlsx'

def parse_shared_strings(zf):
    strings = []
    try:
        with zf.open('xl/sharedStrings.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            # Namespace usually: {http://schemas.openxmlformats.org/spreadsheetml/2006/main}
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            for si in root.findall('main:si', ns):
                # Try to find 't' directly or inside 'r' runs
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
        print("No shared strings found.")
    return strings

def parse_hyperlinks(zf):
    links = {} # Maps rId to Target
    try:
        with zf.open('xl/worksheets/_rels/sheet1.xml.rels') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            # Namespace for relationships
            ns = {'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
            
            for rel in root.findall('rel:Relationship', ns):
                if rel.attrib.get('Type').endswith('/hyperlink'):
                    links[rel.attrib.get('Id')] = rel.attrib.get('Target')
    except KeyError:
        print("No hyperlinks found.")
    return links

def parse_sheet(zf, strings, links_map):
    rows = []
    with zf.open('xl/worksheets/sheet1.xml') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        # Build a map of cell coordinates to hyperlinks if available in the sheet xml
        # Hyperlinks in sheet1.xml link cells to rIds
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
            row_vals = []
            for c in row.findall('main:c', ns):
                ref = c.attrib.get('r') # e.g., A1
                t = c.attrib.get('t')   # type: s=shared string
                v = c.find('main:v', ns)
                
                val = ""
                if v is not None:
                    if t == 's':
                        idx = int(v.text)
                        val = strings[idx]
                    else:
                        val = v.text
                
                # Check for hyperlink
                link = cell_hyperlinks.get(ref)
                
                row_vals.append({
                    'ref': ref,
                    'value': val,
                    'link': link
                })
            rows.append(row_vals)
    return rows

try:
    with zipfile.ZipFile(file_path, 'r') as zf:
        print("Parsing XLSX manually...")
        strings = parse_shared_strings(zf)
        links_map = parse_hyperlinks(zf)
        rows = parse_sheet(zf, strings, links_map)
        
        print(f"Found {len(rows)} rows.")
        
        # Determine columns from first row (assuming it's a header)
        if len(rows) > 0:
            header_row = rows[0]
            print("Headers:")
            for cell in header_row:
                print(f"  {cell['ref']}: {cell['value']}")
        
        # Print sample data from first 5 rows
        for i, row in enumerate(rows[1:6]):
            print("\nRow " + str(i+1) + ":")
            for cell in row:
                if cell['value'] or cell['link']:
                    link_str = f" [LINK: {cell['link']}]" if cell['link'] else ""
                    print(f"  {cell['ref']} ({cell['value']}){link_str}")

except Exception as e:
    print(f"Error parsing XLSX: {e}")

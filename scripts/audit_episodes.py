
import json
import os
import re

DB_PATH = 'shared/episodes_database.json'
NEW_DATA_PATH = 'scripts/new_data.txt'

def parse_new_data():
    with open(NEW_DATA_PATH, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]
    
    episodes = []
    current_ep = {}
    
    # Simple state machine parser
    # Structure seems to be: Title, Date, Time, Link (sometimes extra text)
    # But filtering the text I saved might be cleaner.
    
    # Actually, the file I saved is a filtered version I manually cleaned up in the `CodeContent` above.
    # It has blocks of 4 lines roughly: Title, Date, Time, Link.
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("BandaWeb3") or line.startswith("Inauguración"):
            title = line
            # Extract number if present
            match = re.search(r'#(\d+)', title)
            number = match.group(1) if match else "SPECIAL"
            
            # Next line should be date
            if i+1 < len(lines):
                date_str = lines[i+1]
            else:
                date_str = "Unknown"
                
            # Next line should be time
            if i+2 < len(lines):
                time_str = lines[i+2]
            else:
                time_str = "Unknown"
                
            # Next line link
            if i+3 < len(lines):
                link = lines[i+3]
            else:
                link = ""
                
            episodes.append({
                "number": number,
                "title": title,
                "date": date_str,
                "time": time_str,
                "link": link
            })
            # Advance index. Sometimes there are 4 lines, sometimes 3? 
            # In my cleaned file, it looks consistently 4 lines per block separated by blank lines (which I stripped).
            # Wait, `lines` has no blank lines.
            # So I need to be careful.
            # My saved file has:
            # Title
            # Date
            # Time
            # Link
            # (Loop)
            
            i += 4
        else:
            i += 1
            
    return episodes

def audit():
    new_eps = parse_new_data()
    
    with open(DB_PATH, 'r') as f:
        db = json.load(f)
        
    db_eps = {ep.get('number'): ep for ep in db.get('episodes', [])}
    
    missing = []
    updates = []
    matches = []
    
    print(f"DEBUG: Found {len(new_eps)} episodes in text.")
    
    for ep in new_eps:
        num = ep['number']
        if num == "SPECIAL":
            # Handle special events
            continue
            
        if num not in db_eps:
            missing.append(ep)
        else:
            # Check for major diffs (optional)
            matches.append(ep)
            
    print(f"--- REPORTE DE AUDITORÍA ---")
    print(f"Episodios Nuevos (Faltantes en DB): {len(missing)}")
    if missing:
        print(f"Ejemplos: #{missing[0]['number']} {missing[0]['title']} ... #{missing[-1]['number']} {missing[-1]['title']}")
        print("Lista completa de faltantes:")
        for m in missing:
            print(f"- #{m['number']}: {m['title']} ({m['date']})")
    
    print(f"\nEpisodios Ya Existentes: {len(matches)}")
    print(f"Total en Lista Proporcionada: {len(new_eps)}")

if __name__ == "__main__":
    audit()

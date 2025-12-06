import json
import re
from pathlib import Path
from datetime import datetime

# Based on checks, Ep 30 was likely early 2024.
# The dates in the file are "May 15", "Feb 4".
# Since list goes down to Feb 4, and Ep 30 exists.. let's assume 2024.
# Feb 4 2024.
# May 15 2024.

def parse_date(date_str):
    try:
        # e.g. May 15
        dt = datetime.strptime(date_str + " 2024", "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
    
    existing_nums = {ep["number"]: ep for ep in db["episodes"]}
    
    txt_path = Path("website/inputs/user_list_numbered_2.txt")
    with open(txt_path, "r") as f:
        lines = f.readlines()
    
    new_eps = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        # Look for Title line "BandaWeb3 #057..."
        match = re.search(r"BandaWeb3 #(\d+)", line)
        if match:
            num = match.group(1)
            title = line
            
            # Find Metadata line "es - Ended: May 15..."
            date_str = ""
            duration = ""
            # Usuually next line
            if i+1 < len(lines) and "Ended:" in lines[i+1]:
                meta = lines[i+1]
                try:
                    parts = meta.split("Ended:")[1].split("-")
                    date_str = parts[0].strip()
                    for p in parts:
                        if "Duration:" in p:
                            duration = p.split("Duration:")[1].strip()
                except:
                    pass
            
            # 2024 assumption
            date_iso = parse_date(date_str)
            
            # Check listeners (line after meta or 2 lines after?)
            # Format: 
            # Title
            # Meta
            # Tags
            # Listeners
            # PLAY
            
            listeners = ""
            # Look ahead for PLAY/REPLAY
            for j in range(i+1, i+10):
                if j >= len(lines): break
                if "PLAY" in lines[j] or "REPLAY" in lines[j]:
                    # Line before is likely listeners
                    l_cand = lines[j-1].strip()
                    if l_cand.isdigit(): 
                        listeners = l_cand
                    else:
                        # Extract from current line?
                        m = re.search(r"(\d+)\s+(?:PLAY|REPLAY)", lines[j])
                        if m: listeners = m.group(1)
                    break
            
            # Skip if exists?
            if num in existing_nums:
                # Update listeners if missing?
                ep = existing_nums[num]
                if listeners and not ep.get("listeners"):
                    ep["listeners"] = listeners
                    # print(f"Updated listeners for #{num}")
                continue
                
            guests = re.findall(r"@(\w+)", title)
            guest_links = {g: f"https://x.com/{g}" for g in guests}

            new_ep = {
                "number": num,
                "title": title,
                "date": date_iso,
                "duration": duration,
                "guests": guests,
                "guest_links": guest_links,
                "space_url": "", 
                "description": title,
                "topics": [],
                "status": "archived",
                "transcript_available": False,
                "content_generated": False,
                "flyer_urls": [],
                "listeners": listeners
            }
            new_eps.append(new_ep)
            existing_nums[num] = new_ep # Prevent duplicates in same batch

    print(f"Found {len(new_eps)} new numbered episodes (38-57).")
    
    if new_eps:
        db["episodes"].extend(new_eps)
        # Sort
        def sort_key(ep):
            try:
                return datetime.strptime(ep["date"], "%Y-%m-%d")
            except:
                return datetime.min
        db["episodes"].sort(key=sort_key, reverse=True)
        
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Database updated with numbered batch 2.")

if __name__ == "__main__":
    main()

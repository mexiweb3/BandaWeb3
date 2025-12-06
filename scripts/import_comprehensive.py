import json
import re
from pathlib import Path
from datetime import datetime

# Logic:
# Parse all episodes.
# Matches "BandaWeb3 #XXX".
# If XXX > 30, it is 2025.
# If XXX <= 30, it is 2024.
# (Except known anomalies, but this checks out so far: Ep 30 was Dec 2024).
# Also handle non-numbered hosted spaces (dates in 2024, 2023).

def parse_date(date_str, year):
    try:
        # e.g. May 15
        dt = datetime.strptime(f"{date_str} {year}", "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
    
    # Map existing by number to update
    existing_nums = {ep["number"]: ep for ep in db["episodes"]}
    
    txt_path = Path("website/inputs/user_list_comprehensive.txt")
    with open(txt_path, "r") as f:
        lines = f.readlines()
    
    new_eps = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for Numbered Episodes first
        match = re.search(r"BandaWeb3 [-#]+ ?0?(\d+)", line, re.IGNORECASE)
        if match:
            num_str = match.group(1).zfill(3)
            title = line
            
            # Find Metadata
            # Look ahead a few lines
            date_str = ""
            duration = ""
            full_date_match = None
            
            for k in range(1, 5):
                if i+k >= len(lines): break
                next_l = lines[i+k].strip()
                if "Ended:" in next_l:
                    # Check if explicit year
                    # "Ended: Dec 20 2024"
                    try:
                        pts = next_l.split("Ended:")[1].split("-")
                        date_raw = pts[0].strip()
                        
                        # Explicit year?
                        if re.search(r"\d{4}", date_raw):
                            # Parse as is
                            try:
                                dt = datetime.strptime(date_raw, "%b %d %Y")
                                date_iso = dt.strftime("%Y-%m-%d")
                            except:
                                date_iso = None
                        else:
                            # Implicit year
                            # Rule: > 30 = 2025, <= 30 = 2024
                            # Exception: text might span earlier?
                            if int(num_str) > 30:
                                year = 2025
                            else:
                                year = 2024
                            date_iso = parse_date(date_raw, year)
                            
                        # Duration
                        for p in pts:
                            if "Duration:" in p:
                                duration = p.split("Duration:")[1].strip()
                                
                    except:
                        pass
                    break
            
            # Listeners
            listeners = ""
            for j in range(i+1, i+15):
                if j >= len(lines): break
                if "PLAY" in lines[j] or "REPLAY" in lines[j]:
                    # Line before
                    cand = lines[j-1].strip()
                    if cand.isdigit():
                        listeners = cand
                    break
            
            # Guests
            guests = re.findall(r"@(\w+)", title)
            guest_links = {g: f"https://x.com/{g}" for g in guests}

            
            # Update or Add
            if num_str in existing_nums:
                ep = existing_nums[num_str]
                # Update date if we have a better one (specifically to fix the 2024->2025 error)
                if date_iso:
                     ep["date"] = date_iso
                if listeners:
                    ep["listeners"] = listeners
                # print(f"Updated #{num_str} date to {date_iso}")
                
            else:
                new_ep = {
                    "number": num_str,
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
                existing_nums[num_str] = new_ep

    print(f"Processed comprehensive list. Found {len(new_eps)} NEW numbered episodes.")
    
    if new_eps:
        db["episodes"].extend(new_eps)
        
    # Sort
    def sort_key(ep):
        try:
            return datetime.strptime(ep["date"], "%Y-%m-%d")
        except:
            if ep["date"] and len(ep["date"]) == 4: # Year only
                 return datetime.strptime(ep["date"], "%Y")
            return datetime.min
            
    db["episodes"].sort(key=sort_key, reverse=True)
    
    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print("Database updated with comprehensive list.")

if __name__ == "__main__":
    main()

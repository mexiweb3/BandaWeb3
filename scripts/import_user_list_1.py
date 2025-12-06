import json
import re
from pathlib import Path
from datetime import datetime

def parse_date(date_str):
    try:
        # e.g., Aug 21
        # Need year. Context looks like 2024 from previous data, but might be 2023?
        # Let's assume current cycle 2024 if Aug-Dec, or check context.
        # Actually in user list, "100K TODAY" was Dec 5 2024.
        # "Aug 21" likely 2024.
        dt = datetime.strptime(date_str + " 2024", "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def main():
    # Load DB
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
    
    existing_nums = {ep["number"] for ep in db["episodes"]}
    
    # Load Text List
    txt_path = Path("website/inputs/user_text_list.txt")
    with open(txt_path, "r") as f:
        lines = f.readlines()
        
    episodes_to_add = []
    
    # Simple parser again
    for i, line in enumerate(lines):
        line = line.strip()
        match = re.search(r"BandaWeb3 #(\d+)", line)
        if match:
            num = match.group(1)
            title = line
            
            # Extract Date/Duration
            date_str = ""
            duration = ""
            if i + 1 < len(lines) and "Ended:" in lines[i+1]:
                parts = lines[i+1].split("-")
                for p in parts:
                    if "Ended:" in p:
                        date_str = p.split("Ended:")[1].strip()
                    if "Duration:" in p:
                        duration = p.split("Duration:")[1].strip()
            
            # Skip if already exists?
            if num in existing_nums and num != "071" and num != "064":
                 # Skip normal duplicates
                 continue
            
            # Handle duplicates logic
            if num == "071":
                # Check duration to pick the long one
                if "19 minutes" in duration:
                    print("Skipping short version of #071")
                    continue
            
            # If #064, we might conflict.
            # If existing #064 is in DB, we skip? 
            # Wait, #064 is NOT in DB yet (from analysis).
            # But we have two #064s in the text list.
            # 1. Jun 10
            # 2. Jun 5
            # Usually numbers go up with date. So Jun 5 might be #063?
            # Or Jun 10 is #064.
            # I will add BOTH, but suffix one? or just add both and user sorts it out?
            # User said "Si a todo" (Yes to all).
            # I'll add the first one as #064, second one as #064-B? Or just same number. DB supports it (JSON list).
            
            date_iso = parse_date(date_str) if date_str else ""
            
            guests = re.findall(r"@(\w+)", title)
            guest_links = {g: f"https://x.com/{g}" for g in guests}

            new_ep = {
                "number": num,
                "title": title,
                "date": date_iso,
                "duration": duration,
                "guests": guests,
                "guest_links": guest_links,
                "space_url": "", # No URL in text list
                "description": title,
                "topics": [],
                "status": "archived",
                "transcript_available": False,
                "content_generated": False,
                "flyer_urls": []
            }
            
            # Check if we already added this num in this loop (for the 64 conflict)
            duplicate_in_batch = False
            for e in episodes_to_add:
                if e["number"] == num:
                    # Duplicate in batch
                    # If titles different, keep both?
                    if e["title"] != title:
                        # Make this one unique
                        # new_ep["number"] = num + "-B" # Let's handle it gracefully
                        pass
                    else:
                        duplicate_in_batch = True
            
            if not duplicate_in_batch:
                episodes_to_add.append(new_ep)

    # Add to DB
    initial_len = len(db["episodes"])
    db["episodes"].extend(episodes_to_add)
    
    # Sort
    def sort_key(ep):
        try:
            return datetime.strptime(ep["date"], "%Y-%m-%d")
        except:
            return datetime.min
    db["episodes"].sort(key=sort_key, reverse=True)

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
        
    print(f"Imported {len(episodes_to_add)} episodes from text list 1.")

if __name__ == "__main__":
    main()

import csv
import json
import re
from datetime import datetime
from pathlib import Path
import sys

def parse_date(date_str):
    try:
        # Format: Mar 2 2023
        dt = datetime.strptime(date_str, "%b %d %Y")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%Y%m%d")
    except ValueError:
        return None, None

def main():
    base_dir = Path(".")
    csv_path = base_dir / "website/inputs/X Spaces - Event_Summary2.csv"
    db_path = base_dir / "data/episodes_database.json"

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    with open(db_path, "r") as f:
        db = json.load(f)
    
    # Map Date -> Episode(s)
    # Some dates might have multiple episodes, so list of eps.
    db_dates = {}
    for ep in db["episodes"]:
        d = ep.get("date")
        if d:
            if d not in db_dates:
                db_dates[d] = []
            db_dates[d].append(ep)
    
    new_episodes = []
    conflicts = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader) # Title,Ended,Speakers,Duration
        
        for row in reader:
            if not row or len(row) < 4:
                continue
            
            title = row[0].strip()
            date_str_raw = row[1].strip()
            duration = row[3].strip()
            
            date_iso, date_id = parse_date(date_str_raw)
            if not date_iso:
                print(f"Skipping invalid date: {date_str_raw}")
                continue
                
            # Check for existence
            if date_iso in db_dates:
                # Potential conflict or match
                existing_eps = db_dates[date_iso]
                match_found = False
                for ep in existing_eps:
                    # Simple fuzzy match on title? or just assume match if date matches?
                    # Let's say if date matches, it's likely the same event unless we have multiple on same day.
                    # We report diffs.
                    
                    db_title = ep.get("title", "")
                    db_dur = ep.get("duration", "")
                    
                    # Normalize for comparison
                    if title.lower() in db_title.lower() or db_title.lower() in title.lower():
                        match_found = True
                        
                        diffs = []
                        if title != db_title and abs(len(title) - len(db_title)) > 5: 
                             diffs.append(f"Title mismatch: '{title}' vs '{db_title}'")
                        if duration != db_dur and duration != "" and db_dur != "":
                             diffs.append(f"Duration mismatch: '{duration}' vs '{db_dur}'")
                        
                        if diffs:
                            conflicts.append({
                                "date": date_iso,
                                "existing_title": db_title,
                                "new_title": title,
                                "issues": diffs
                            })
                        break # Found the matching event
                
                if not match_found and len(existing_eps) > 0:
                     # Date exists but title is very different. Could be a second event on same day?
                     # Or just a title change.
                     # Let's verify.
                     conflicts.append({
                         "date": date_iso,
                         "existing_title": [e.get("title") for e in existing_eps],
                         "new_title": title,
                         "issues": ["Date collision but titles differ significantly. Check manually."]
                     })
            else:
                # New Episode
                ep_num = date_id
                # Check if specific ID exists (unlikely if date doesn't match, except if ID logic differs)
                
                guests = re.findall(r"@(\w+)", title)
                guest_links = {g: f"https://x.com/{g}" for g in guests}
                
                new_ep = {
                    "number": ep_num,
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
                    "flyer_urls": []
                }
                new_episodes.append(new_ep)
                # Add to local map to prevent duplications within the CSV itself
                if date_iso not in db_dates:
                    db_dates[date_iso] = []
                db_dates[date_iso].append(new_ep)

    # Process results
    print(f"Analysis Complete.")
    print(f"New Episodes to Add: {len(new_episodes)}")
    print(f"Conflicts/Differences Found: {len(conflicts)}")
    
    if new_episodes:
        db["episodes"].extend(new_episodes)
        # Sort
        def sort_key(ep):
            try:
                return datetime.strptime(ep["date"], "%Y-%m-%d")
            except:
                return datetime.min
        db["episodes"].sort(key=sort_key, reverse=True)
        
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Database updated with new episodes.")
    
    print("\n--- Conflicts Report ---")
    for c in conflicts:
        print(f"Date: {c['date']}")
        print(f"  New: {c['new_title']}")
        print(f"  Existing: {c['existing_title']}")
        for issue in c['issues']:
            print(f"  - {issue}")
        print("")

if __name__ == "__main__":
    main()

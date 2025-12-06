import csv
import json
import re
from datetime import datetime
from pathlib import Path
import sys

def parse_date(date_str):
    try:
        # Format: Dec 5 2024
        dt = datetime.strptime(date_str, "%b %d %Y")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%Y%m%d")
    except ValueError:
        return None, None

def main():
    base_dir = Path(".")
    csv_path = base_dir / "website/inputs/X Spaces - Sheet7.csv"
    db_path = base_dir / "data/episodes_database.json"

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    with open(db_path, "r") as f:
        db = json.load(f)
    
    # Map Date -> List of Episodes
    db_dates = {}
    for ep in db["episodes"]:
        d = ep.get("date")
        if d:
            if d not in db_dates:
                db_dates[d] = []
            db_dates[d].append(ep)
    
    new_episodes = []
    conflicts = []
    updated_links = 0
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        # No header skipping per se, row 1 is likely empty or headers.
        
        for row in reader:
            # We expect mainly columns 2 (Title), 3 (Date), 5 (Duration), 8 (Link)
            # Indices: 0, 1, 2, 3, 4, 5, 6, 7, 8
            if not row or len(row) < 9:
                continue
            
            title = row[2].strip()
            date_str_raw = row[3].strip()
            duration = row[5].strip()
            link = row[8].strip()
            
            if not title or not date_str_raw:
                continue
            
            date_iso, date_id = parse_date(date_str_raw)
            if not date_iso:
                # print(f"Skipping invalid date row: {title} - {date_str_raw}")
                continue
            
            # Check existence
            if date_iso in db_dates:
                existing_eps = db_dates[date_iso]
                match_found = False
                
                for ep in existing_eps:
                    db_title = ep.get("title", "")
                    
                    # Fuzzy match title
                    # Normalizing
                    t1 = re.sub(r'\W+', '', title.lower())
                    t2 = re.sub(r'\W+', '', db_title.lower())
                    
                    if t1 in t2 or t2 in t1 or (len(t1) > 10 and t1[:10] == t2[:10]):
                        match_found = True
                        # Update Link if missing
                        if link and (not ep.get("space_url") or ep["space_url"] == ""):
                            ep["space_url"] = link
                            updated_links += 1
                        break
                
                if not match_found:
                    # Date match but title different.
                    # Could be a second event on same day.
                    # Treat as potential conflict or new episode?
                    # User asked to "add spaces that you don't have".
                    # If the title is very different, assume it's a different Space on the same day.
                    # But also report it so user knows.
                    
                    # Check if we should add it
                    conflicts.append({
                        "date": date_iso,
                        "existing_titles": [e.get("title") for e in existing_eps],
                        "new_title": title,
                        "action": "Adding as new episode (Date collision)"
                    })
                    
                    # Add as new
                    ep_num = f"{date_id}-S7" # Suffix to avoid ID collision
                    
                    guests = re.findall(r"@(\w+)", title)
                    guest_links = {g: f"https://x.com/{g}" for g in guests}

                    new_ep = {
                        "number": ep_num,
                        "title": title,
                        "date": date_iso,
                        "duration": duration,
                        "guests": guests,
                        "guest_links": guest_links,
                        "space_url": link,
                        "description": title,
                        "topics": [],
                        "status": "archived",
                        "transcript_available": False,
                        "content_generated": False,
                        "flyer_urls": []
                    }
                    new_episodes.append(new_ep)
                    db_dates[date_iso].append(new_ep)
                    
            else:
                # Totally new date
                ep_num = date_id
                
                guests = re.findall(r"@(\w+)", title)
                guest_links = {g: f"https://x.com/{g}" for g in guests}

                new_ep = {
                    "number": ep_num,
                    "title": title,
                    "date": date_iso,
                    "duration": duration,
                    "guests": guests,
                    "guest_links": guest_links,
                    "space_url": link,
                    "description": title,
                    "topics": [],
                    "status": "archived",
                    "transcript_available": False,
                    "content_generated": False,
                    "flyer_urls": []
                }
                new_episodes.append(new_ep)
                if date_iso not in db_dates:
                    db_dates[date_iso] = []
                db_dates[date_iso].append(new_ep)

    # Dedup new episodes within the list itself? (CSV might have duplicates)
    # The loop adds to db_dates immediately so duplicates in CSV logic above handles it (it will match the one just added).
    
    print(f"Analysis Complete.")
    print(f"New Episodes to Add: {len(new_episodes)}")
    print(f"Existing Episodes Updated with Links: {updated_links}")
    print(f"Conflicts/Date Collisions: {len(conflicts)}")

    if new_episodes or updated_links > 0:
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
        print("Database updated.")
    
    if conflicts:
        print("\n--- Date Collisions (Added as New) ---")
        for c in conflicts:
            print(f"Date: {c['date']}")
            print(f"  New: {c['new_title']}")
            print(f"  Existing: {c['existing_titles']}")
            print("")

if __name__ == "__main__":
    main()

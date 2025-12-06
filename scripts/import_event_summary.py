import csv
import json
import re
from datetime import datetime
from pathlib import Path

def parse_date(date_str):
    try:
        # Format: Feb 28 2023
        dt = datetime.strptime(date_str, "%b %d %Y")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%Y%m%d")
    except ValueError:
        return date_str, None

def main():
    base_dir = Path(".")
    csv_path = base_dir / "website/inputs/X Spaces - Event_Summary.csv"
    db_path = base_dir / "data/episodes_database.json"

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    with open(db_path, "r") as f:
        db = json.load(f)
    
    # Create a map of existing dates/IDs to avoid duplicates if possible
    existing_nums = {ep["number"] for ep in db["episodes"]}
    existing_dates = {ep["date"] for ep in db["episodes"]} # Not perfectly unique but helps

    new_episodes_count = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader) # Title,Ended,Speakers,Duration
        
        for row in reader:
            if not row or len(row) < 4:
                continue
                
            title_col = row[0]
            ended_col = row[1]
            # speakers_col = row[2] # Just a count
            duration_col = row[3]
            
            date_str, date_id = parse_date(ended_col)
            
            if not date_id:
                # print(f"Skipping row with invalid date: {ended_col}")
                continue
            
            # ID Generation Strategy: YYYYMMDD
            # Check collision
            ep_num = date_id
            suffix = 0
            while ep_num in existing_nums:
                suffix += 1
                ep_num = f"{date_id}-{suffix}"
            
            # If we already have an episode on this date in DB, maybe we should skip?
            # The CSV might contain duplicates of what we just imported from Sheet5 (which was more recent).
            # Sheet5 had dates like "Jan 9 2025" back to "Aug 29 2024" etc.
            # This CSV seems to go back to 2021.
            # If the date is already in existing_dates, let's be careful.
            # Actually, "Event_Summary" seems to be older stuff mostly.
            # Let's import additively for now, as user requested "Import these".
            
            # Extract Guests from Title
            guests = re.findall(r"@(\w+)", title_col)
            
            guest_links = {}
            for g in guests:
                guest_links[g] = f"https://x.com/{g}"
            
            new_ep_data = {
                "number": ep_num,
                "title": title_col.strip(),
                "date": date_str,
                "duration": duration_col,
                "guests": guests,
                "guest_links": guest_links,
                "space_url": "", # Not in this CSV
                "description": title_col.strip(), # No desc, use title
                "topics": [],
                "status": "archived",
                "transcript_available": False,
                "content_generated": False,
                "flyer_urls": []
            }
            
            db["episodes"].append(new_ep_data)
            existing_nums.add(ep_num) # Track newly added ID
            new_episodes_count += 1

    # Sort episodes by date descending
    def sort_key(ep):
        try:
            return datetime.strptime(ep["date"], "%Y-%m-%d")
        except:
            return datetime.min

    db["episodes"].sort(key=sort_key, reverse=True)

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

    print(f"Import complete: {new_episodes_count} historical episodes added.")

if __name__ == "__main__":
    main()

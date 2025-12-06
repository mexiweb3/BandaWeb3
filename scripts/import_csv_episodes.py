import csv
import json
import re
from datetime import datetime
from pathlib import Path

def parse_date(date_str):
    try:
        # Format: Jan 9 2025
        dt = datetime.strptime(date_str, "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return date_str

def main():
    base_dir = Path(".")
    csv_path = base_dir / "website/inputs/X Spaces - Sheet5.csv"
    db_path = base_dir / "data/episodes_database.json"

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    with open(db_path, "r") as f:
        db = json.load(f)
    
    # Create a map of existing episodes for easier updating
    ep_map = {ep["number"]: ep for ep in db["episodes"]}
    
    new_episodes_count = 0
    updated_episodes_count = 0

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader) # Skip header
        # Expected header: Host,Space Name,Title,Ended,Speakers,Duration,Participants,Space Link
        
        for row in reader:
            if not row or len(row) < 8:
                continue
                
            title_col = row[2]
            ended_col = row[3]
            duration_col = row[5]
            link_col = row[7]
            
            # Extract Episode Number
            match_num = re.search(r"BandaWeb3\s*#(\d+)", title_col, re.IGNORECASE)
            if not match_num:
                # Try finding just #XXX
                match_num = re.search(r"#(\d+)", title_col)
            
            if not match_num:
                # print(f"Skipping row: Could not extract episode number from '{title_col}'")
                continue
                
            ep_num = match_num.group(1)
            
            # Extract Guest
            guests = []
            match_guest = re.search(r"@(\w+)", title_col)
            if match_guest:
                guests.append(match_guest.group(1))
            
            # Additional guests might be present, but let's stick to the first one for now or split if needed.
            # Some titles have multiple @, e.g. "@arbitrum @eth_mty @mxweb3"
            guests = re.findall(r"@(\w+)", title_col)
            
            date_str = parse_date(ended_col)
            
            # Construct guest links
            guest_links = {}
            for g in guests:
                guest_links[g] = f"https://x.com/{g}"

            # Basic description if missing
            description = f"Episode {ep_num} of BandaWeb3. " + title_col
            
            # Episode Object
            new_ep_data = {
                "number": ep_num,
                "title": title_col.strip() or f"Episode {ep_num}",
                "date": date_str,
                "duration": duration_col,
                "guests": guests,
                "guest_links": guest_links,
                "space_url": link_col,
                "description": description,
                "topics": [],
                "status": "published",
                "transcript_available": False,
                "content_generated": False,
                # Preserve existing flyer/unlock if present, otherwise empty default?
                # Actually, we should check if they exist first.
            }
            
            if ep_num in ep_map:
                # Update existing
                existing = ep_map[ep_num]
                # Only update fields that are new or better? 
                # User said "add these episodes". Assuming CSV is source of truth for these specific fields.
                # Preserve manual fields like unlock_url, opensea_url, flyer_urls if they exist in DB but not CSV (CSV doesn't have them)
                
                # Update keys
                existing["date"] = new_ep_data["date"]
                existing["duration"] = new_ep_data["duration"]
                existing["space_url"] = new_ep_data["space_url"]
                
                # If existing has guests/title, maybe keep them if they are richer? 
                # The CSV title is pretty good. "BandaWeb3 #032 @betsacarrizo"
                if existing["title"] == "Pending Title" or not existing["title"]:
                     existing["title"] = new_ep_data["title"]
                     
                if not existing["guests"] and new_ep_data["guests"]:
                    existing["guests"] = new_ep_data["guests"]
                    existing["guest_links"] = new_ep_data["guest_links"]

                updated_episodes_count += 1
            else:
                # Create new
                new_ep_data["flyer_urls"] = [] # Default empty
                db["episodes"].append(new_ep_data)
                ep_map[ep_num] = new_ep_data # Add to map for order check?
                new_episodes_count += 1

    # Sort episodes by number descending (optional, but good for JSON organization)
    # db["episodes"].sort(key=lambda x: int(x["number"]) if x["number"].isdigit() else 0, reverse=True)

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

    print(f"Import complete: {new_episodes_count} new, {updated_episodes_count} updated.")

if __name__ == "__main__":
    main()

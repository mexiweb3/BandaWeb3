import json
from datetime import datetime
from pathlib import Path

# Data from user
raw_data = """
#019	28 Nov 2024
#020	29 Nov 2024
#021	3 Dec 2024
#022	5 Dec 2024
#023	6 Dec 2024
#024	10 Dec 2024
#025	12 Dec 2024
#026	13 Dec 2024
#027	17 Dec 2024
#028	TBD
#029	20 Dec 2024
"""

def parse_date(date_str):
    if "TBD" in date_str.upper():
        return "TBD"
    return datetime.strptime(date_str.strip(), "%d %b %Y").strftime("%Y-%m-%d")

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    new_formatted_episodes = []
    
    # Parse the raw text
    lines = [line.strip() for line in raw_data.strip().split('\n') if line.strip()]
    
    # Pre-process lines to handle "#Number Date" format
    processed_lines = []
    for line in raw_data.strip().split('\n'):
        line = line.strip()
        if not line: continue
        
        parts = line.split(maxsplit=1)
        if len(parts) == 2 and parts[0].startswith("#"):
            processed_lines.append(parts[0]) # Number
            processed_lines.append(parts[1]) # Date
        else:
            processed_lines.append(line)

    current_ep = {}
    for line in processed_lines:
        if line.startswith("#"):
            if current_ep:
                new_formatted_episodes.append(current_ep)
            current_ep = {
                "number": line.replace("#", ""),
                "title": "Pending Title", # Placeholder
                "date": "",
                "guests": [],
                "duration": "Pending",
                "description": "Details pending...",
                "topics": [],
                "status": "pending",
                "transcript_available": False,
                "content_generated": False,
                "space_url": "",
                "audio_url": "",
                "flyer_urls": []
            }
        else:
            # Assume date line
            try:
                current_ep["date"] = parse_date(line)
            except ValueError:
                print(f"Skipping unknown line: {line}")
    
    # Append last one
    if current_ep:
        new_formatted_episodes.append(current_ep)

    # Add to existing episodes (avoiding duplicates)
    existing_nums = {e["number"] for e in db["episodes"]}
    
    for ep in new_formatted_episodes:
        if ep["number"] not in existing_nums:
            db["episodes"].append(ep)
            print(f"Added Episode {ep['number']}")
        else:
            print(f"Episode {ep['number']} already exists. Skipping.")

    # Sort episodes by number descending (optional, but good for display)
    db["episodes"].sort(key=lambda x: x["number"], reverse=True)
    
    # Update stats
    db["stats"]["total_episodes"] = len(db["episodes"])

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    print("Database updated successfully.")

if __name__ == "__main__":
    main()

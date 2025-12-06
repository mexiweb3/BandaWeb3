import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    # Check if 072 exists
    ep_072 = None
    for ep in db["episodes"]:
        if ep["number"] == "072":
            ep_072 = ep
            break
    
    new_data = {
        "number": "072",
        "title": "Episode 072 with @xenonnel",
        "date": "2025-09-04", # Jueves 4 Sep (2025 is Thursday)
        "time": "12:00 PM CST",
        "duration": "60 min",
        "guests": ["xenonnel"],
        "guest_links": {"xenonnel": "https://x.com/xenonnel"}, # Inferred
        "description": "Xenonnel y yo estaremos platicando de lo sucedido en la Stablecoin Conference y todos los side events. Mientras platicamos estaremos jugando en @yeet, el casino online que ha sobrepasado $500M USD en volúmen en 5 meses.",
        "topics": ["Stablecoin Conference", "Yeet", "Casino"],
        "status": "scheduled",
        "space_url": "", # No space URL provided
        "unlock_url": "",
        "opensea_url": "",
        "contract_url": "",
        "flyer_urls": ["../static/images/flyer_072.jpg"],
        "transcript_available": False,
        "content_generated": False
    }

    if ep_072:
        ep_072.update(new_data)
        print("Updated existing Episode 072.")
    else:
        # Insert in correct order? Or just append.
        # Let's try to insert after 073 if possible, but the list is mixed.
        # Just insert at position 2 (after 074, 073).
        db["episodes"].insert(2, new_data)
        print("Created new Episode 072.")

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()

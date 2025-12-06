import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "074":
            # Append new images if not already present
            existing_flyers = ep.get("flyer_urls", [])
            new_flyers = ["../static/images/flyer_074_4.jpg", "../static/images/flyer_074_5.jpg"]
            
            for flyer in new_flyers:
                if flyer not in existing_flyers:
                    existing_flyers.append(flyer)
            
            ep["flyer_urls"] = existing_flyers
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 074 images.")
    else:
        print("Episode 074 not found.")

if __name__ == "__main__":
    main()

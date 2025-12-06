import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "001":
            ep["flyer_urls"] = ["../static/images/flyer_001.png"]
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 001 flyer.")
    else:
        print("Episode 001 not found.")

if __name__ == "__main__":
    main()

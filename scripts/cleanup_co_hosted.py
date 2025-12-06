
import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    # Filter out episodes that look like the ones we just added
    # They have description starting with "Co-hosted Space:"
    # Or just based on the ID format logic used previously?
    # Description is safer.
    
    original_count = len(db["episodes"])
    
    db["episodes"] = [ep for ep in db["episodes"] if not ep.get("description", "").startswith("Co-hosted Space:")]
    
    new_count = len(db["episodes"])
    print(f"Removed {original_count - new_count} episodes.")
    
    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()

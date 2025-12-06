import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "006" and not ep.get("date"):
            ep["date"] = "2024-10-17"
            print("Restored date for Ep 006")
            updated = True
        elif ep["number"] == "015" and not ep.get("date"):
            ep["date"] = "2024-11-19"
            print("Restored date for Ep 015")
            updated = True
            
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Database updated.")
    else:
        print("No fixes needed.")

if __name__ == "__main__":
    main()

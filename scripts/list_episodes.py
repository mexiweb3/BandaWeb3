import json
from pathlib import Path
from datetime import datetime

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    episodes = db["episodes"]
    
    # Sort by date descending
    def get_date(ep):
        try:
            return datetime.strptime(ep["date"], "%Y-%m-%d")
        except ValueError:
            return datetime.min

    episodes.sort(key=get_date, reverse=True)

    print(f"Total Episodes: {len(episodes)}\n")
    print(f"{'Date':<12} | {'#':<8} | {'Title'}")
    print("-" * 80)
    for ep in episodes:
        num = ep.get("number", "N/A")
        date = ep.get("date", "Unknown")
        title = ep.get("title", "No Title")
        print(f"{date:<12} | {num:<8} | {title}")

if __name__ == "__main__":
    main()

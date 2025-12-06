import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "004":
            ep["date"] = "2024-09-26" # Jueves 26 de septiembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["natzcalli"]
            ep["guest_links"] = {"natzcalli": "https://x.com/natzcalli"}
            ep["space_url"] = "https://x.com/i/spaces/1kvJpbZXeBQKE"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-004-natzcalli"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-004-natzcalli"
            ep["contract_url"] = "https://arbiscan.io//address/0xfc4fedc093393f46ad12dea9a42f5cb3bc9599a2"
            ep["flyer_urls"] = ["../static/images/flyer_004.png"]
            ep["title"] = "Episode 004 with @natzcalli"
            ep["description"] = "Episode 004 of BandaWeb3 with special guest @natzcalli."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 004 details.")
    else:
        print("Episode 004 not found.")

if __name__ == "__main__":
    main()

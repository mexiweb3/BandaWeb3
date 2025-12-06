import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "005":
            ep["date"] = "2024-10-01" # Martes 1 de octubre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["haycarlitos"]
            ep["guest_links"] = {"haycarlitos": "https://x.com/haycarlitos"}
            ep["space_url"] = "https://x.com/i/spaces/1vOxwrpvWNDJB"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-005-haycarlitos"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-005-haycarlitos"
            ep["contract_url"] = "https://arbiscan.io//address/0x92a623a93351782d74b3e3bfad8dc52d5b33d07b"
            ep["flyer_urls"] = ["../static/images/flyer_005.png"]
            ep["title"] = "Episode 005 with @haycarlitos"
            ep["description"] = "Episode 005 of BandaWeb3 with special guest @haycarlitos."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 005 details.")
    else:
        print("Episode 005 not found.")

if __name__ == "__main__":
    main()

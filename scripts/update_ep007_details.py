import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "007":
            ep["date"] = "2024-10-22" # Martes 22 de octubre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["Yisbelpd"]
            ep["guest_links"] = {"Yisbelpd": "https://x.com/Yisbelpd"}
            ep["space_url"] = "https://x.com/i/spaces/1djxXrZANyNGZ"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-007-yisbelpd"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-007-yisbelpd"
            ep["contract_url"] = "https://arbiscan.io//address/0x4096670d0ccb444d913a42ffbb6eb304a30a174a"
            ep["flyer_urls"] = ["../static/images/flyer_007.png"]
            ep["title"] = "Episode 007 with @Yisbelpd"
            ep["description"] = "Episode 007 of BandaWeb3 with special guest @Yisbelpd."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 007 details.")
    else:
        print("Episode 007 not found.")

if __name__ == "__main__":
    main()

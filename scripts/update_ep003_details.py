import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "003":
            ep["date"] = "2024-09-10" # Martes 10 septiembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["sandym_c"]
            ep["guest_links"] = {"sandym_c": "https://x.com/sandym_c"}
            ep["space_url"] = "https://x.com/i/spaces/1mnxeAPBjqZxX"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-003-sandym-c"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-003-sandym-c"
            ep["contract_url"] = "https://arbiscan.io//address/0x51aca4d171ae39cbffe41f7bb4f4acb725fb481f"
            ep["flyer_urls"] = ["../static/images/flyer_003.png"]
            ep["title"] = "Episode 003 with @sandym_c"
            ep["description"] = "Episode 003 of BandaWeb3 with special guest @sandym_c."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 003 details.")
    else:
        print("Episode 003 not found.")

if __name__ == "__main__":
    main()

import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "001":
            ep["date"] = "2024-08-29" # Jueves 29 agosto 2024
            ep["time"] = "12:00 PM CST" # 12pm 🇲🇽
            ep["guests"] = ["0xKaroShow"]
            ep["guest_links"] = {"0xKaroShow": "https://x.com/0xKaroShow"}
            ep["space_url"] = "https://x.com/i/spaces/1ZkKzRgLvbLKv"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-001-0-x-karo-show"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-001-0xkaroshow"
            ep["contract_url"] = "https://arbiscan.io//address/0xce03e904d588a2a78e7173b19c2fb0eec7a74333"
            ep["title"] = "Episode 001 with @0xKaroShow" # Keeping/Refining title
            ep["description"] = "Episode 001 of BandaWeb3 with special guest @0xKaroShow." # Basic desc if not present
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 001 details.")
    else:
        print("Episode 001 not found.")

if __name__ == "__main__":
    main()

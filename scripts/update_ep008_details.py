import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "008":
            ep["date"] = "2024-10-24" # Jueves 24 de octubre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["jgonzalezferrer"]
            ep["guest_links"] = {"jgonzalezferrer": "https://x.com/jgonzalezferrer"}
            ep["space_url"] = "https://x.com/i/spaces/1MnxnDraMVyGO"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-008-jgonzalezferrer"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-008-jgonzalezferrer"
            ep["contract_url"] = "https://arbiscan.io//address/0xeaabb698890eb77c32353921f3ef072b3a83a776"
            ep["flyer_urls"] = ["../static/images/flyer_008.png"]
            ep["title"] = "Episode 008 with @jgonzalezferrer"
            ep["description"] = "Episode 008 of BandaWeb3 with special guest @jgonzalezferrer."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 008 details.")
    else:
        print("Episode 008 not found.")

if __name__ == "__main__":
    main()

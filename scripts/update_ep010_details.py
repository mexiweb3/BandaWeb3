import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "010":
            ep["date"] = "2024-11-05" # Martes 5 de noviembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["andreweb3_btc"]
            ep["guest_links"] = {"andreweb3_btc": "https://x.com/andreweb3_btc"}
            ep["space_url"] = "https://x.com/i/spaces/1BRJjwWpMeoxw"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-010-andreweb-3-btc"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-010-andreweb3-btc"
            ep["contract_url"] = "https://arbiscan.io//address/0xeee3e810f6b93c5b69912e75970e9a99048f8d54"
            ep["flyer_urls"] = ["../static/images/flyer_010.png"]
            ep["title"] = "Episode 010 with @andreweb3_btc"
            ep["description"] = "Episode 010 of BandaWeb3 with special guest @andreweb3_btc."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 010 details.")
    else:
        print("Episode 010 not found.")

if __name__ == "__main__":
    main()

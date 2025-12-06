import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "006":
            ep["date"] = "2024-10-17" # Jueves 17 de octubre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["MinimalTrader_"]
            ep["guest_links"] = {"MinimalTrader_": "https://x.com/MinimalTrader_"}
            ep["space_url"] = "https://x.com/i/spaces/1BRJjwVWbPVxw"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-004-minimal-trader"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-006-minimaltrader"
            ep["contract_url"] = "https://arbiscan.io//address/0x6dcbe67840c190362242ef31cf909227b1fcb884"
            ep["flyer_urls"] = ["../static/images/flyer_006.png"]
            ep["title"] = "Episode 006 with @MinimalTrader_"
            ep["description"] = "Episode 006 of BandaWeb3 with special guest @MinimalTrader_."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 006 details.")
    else:
        print("Episode 006 not found.")

if __name__ == "__main__":
    main()

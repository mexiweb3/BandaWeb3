import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "009":
            ep["date"] = "2024-10-29" # Martes 29 de octubre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["VizZu11_11"]
            ep["guest_links"] = {"VizZu11_11": "https://x.com/VizZu11_11"}
            ep["space_url"] = "https://x.com/i/spaces/1lDxLlRbwabxm"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-009-viz-zu-11-11"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-009-vizzu11-11"
            ep["contract_url"] = "https://arbiscan.io/address/0x9D09f2e3ABa9096EfE868c100f45F3355F1b522d"
            ep["flyer_urls"] = ["../static/images/flyer_009.png"]
            ep["title"] = "Episode 009 with @VizZu11_11"
            ep["description"] = "Episode 009 of BandaWeb3 with special guest @VizZu11_11."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 009 details.")
    else:
        print("Episode 009 not found.")

if __name__ == "__main__":
    main()

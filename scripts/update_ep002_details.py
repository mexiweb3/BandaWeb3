import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated = False
    for ep in db["episodes"]:
        if ep["number"] == "002":
            ep["date"] = "2024-09-05" # Jueves 5 septiembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["sohobiit"]
            ep["guest_links"] = {"sohobiit": "https://x.com/sohobiit"}
            ep["space_url"] = "https://x.com/i/spaces/1kvJpbwePbwKE"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-002-sohobiit"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-002-sohobiit"
            ep["contract_url"] = "https://arbiscan.io//address/0xfa38f899f453e4f44fd74919a7b0a2adb1859ba0"
            ep["flyer_urls"] = ["../static/images/flyer_002.png"]
            ep["title"] = "Episode 002 with @sohobiit"
            ep["description"] = "Episode 002 of BandaWeb3 with special guest @sohobiit."
            updated = True
            break
    
    if updated:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Updated Episode 002 details.")
    else:
        print("Episode 002 not found.")

if __name__ == "__main__":
    main()

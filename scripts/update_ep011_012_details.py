import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated_count = 0
    for ep in db["episodes"]:
        if ep["number"] == "011":
            ep["date"] = "2024-11-07" # Martes 7 de noviembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["rosaglez_eth"]
            ep["guest_links"] = {"rosaglez_eth": "https://x.com/rosaglez_eth"}
            ep["space_url"] = "https://x.com/i/spaces/1RDGlymzPrMJL"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-011-rosaglez-eth"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-011-rosaglez-eth"
            ep["contract_url"] = "https://arbiscan.io/address/0xBA6031b5ED7e7319524b44C1fE569Cd1Fd822ee8"
            ep["flyer_urls"] = ["../static/images/flyer_011.png"]
            ep["title"] = "Episode 011 with @rosaglez_eth"
            ep["description"] = "Episode 011 of BandaWeb3 with special guest @rosaglez_eth."
            updated_count += 1
        
        elif ep["number"] == "012":
            ep["date"] = "2024-11-12" # Martes 12 de noviembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["asarvide9"]
            ep["guest_links"] = {"asarvide9": "https://x.com/asarvide9"}
            ep["space_url"] = "https://x.com/i/spaces/1lDGLlAnDWkGm"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-012-asarvide-9"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-012-asarvide9"
            ep["contract_url"] = "https://arbiscan.io/address/0x419e452E15A0e52D9B6afC04Acbae4aC9C92Bbe9"
            ep["flyer_urls"] = ["../static/images/flyer_012.png"]
            ep["title"] = "Episode 012 with @asarvide9"
            ep["description"] = "Episode 012 of BandaWeb3 with special guest @asarvide9."
            updated_count += 1

    if updated_count > 0:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print(f"Updated {updated_count} episodes (011 & 012).")
    else:
        print("Episodes 011 and 012 not found.")

if __name__ == "__main__":
    main()

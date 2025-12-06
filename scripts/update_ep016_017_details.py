import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated_count = 0
    for ep in db["episodes"]:
        if ep["number"] == "016":
            ep["date"] = "2024-11-21" # Jueves 21 noviembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["eddiespino"]
            ep["guest_links"] = {"eddiespino": "https://x.com/eddiespino"}
            ep["space_url"] = "https://x.com/i/spaces/1ynKODANPyvGR"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-016-eddiespino"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-016-eddiespino"
            ep["contract_url"] = "https://arbiscan.io//address/0xc057bf08093580ac43380b14d026e4e1ade3bd73"
            ep["flyer_urls"] = ["../static/images/flyer_016.png"]
            ep["title"] = "Episode 016 with @eddiespino"
            ep["description"] = "Episode 016 of BandaWeb3 with special guest @eddiespino."
            updated_count += 1
        
        elif ep["number"] == "017":
            ep["date"] = "2024-11-22" # Viernes 22 noviembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["CryptoNotaz"]
            ep["guest_links"] = {"CryptoNotaz": "https://x.com/CryptoNotaz"}
            ep["space_url"] = "https://x.com/i/spaces/1PlJQbrdMXXxE"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-017-crypto-notaz"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-017-cryptonotaz"
            ep["contract_url"] = "https://arbiscan.io/address/0x7c5e1577e19e34a70ea9b8d38e46374e8b21c5c2"
            ep["flyer_urls"] = ["../static/images/flyer_017.png"]
            ep["title"] = "Episode 017 with @CryptoNotaz"
            ep["description"] = "Episode 017 of BandaWeb3 with special guest @CryptoNotaz."
            updated_count += 1

    if updated_count > 0:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print(f"Updated {updated_count} episodes (016 & 017).")
    else:
        print("Episodes 016 and 017 not found.")

if __name__ == "__main__":
    main()

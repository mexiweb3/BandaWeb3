import json
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated_count = 0
    for ep in db["episodes"]:
        if ep["number"] == "013":
            ep["date"] = "2024-11-14" # Jueves 14 noviembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["AndriuJose20"]
            ep["guest_links"] = {"AndriuJose20": "https://x.com/AndriuJose20"}
            ep["space_url"] = "https://x.com/i/spaces/1nAKEpWrVXaxL"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-013-andriu-jose-20"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-013-andriujose20"
            ep["contract_url"] = "https://arbiscan.io/address/0x3e0d119edd647BC79afeA106e75ABA7717D61Ec9"
            ep["flyer_urls"] = ["../static/images/flyer_013.png"]
            ep["title"] = "Episode 013 with @AndriuJose20"
            ep["description"] = "Episode 013 of BandaWeb3 with special guest @AndriuJose20."
            updated_count += 1
        
        elif ep["number"] == "014":
            ep["date"] = "2024-08-18" # Lunes 18 agosto 2024
            ep["time"] = "06:00 PM CST" # 6pm
            ep["guests"] = ["AnanaNFTs"]
            ep["guest_links"] = {"AnanaNFTs": "https://x.com/AnanaNFTs"}
            ep["space_url"] = "https://x.com/i/spaces/1lDxLlabMdoxm"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-015-anana-nf-ts"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-014-anananfts"
            ep["contract_url"] = "https://arbiscan.io//address/0x0147aa70c8caa8a47e98808bca207c94a3beca8a"
            ep["flyer_urls"] = ["../static/images/flyer_014.png"]
            ep["title"] = "Episode 014 with @AnanaNFTs"
            ep["description"] = "Episode 014 of BandaWeb3 with special guest @AnanaNFTs."
            updated_count += 1

        elif ep["number"] == "015":
            ep["date"] = "2024-11-19" # Martes 19 noviembre 2024
            ep["time"] = "12:00 PM CST"
            ep["guests"] = ["Atitovva"]
            ep["guest_links"] = {"Atitovva": "https://x.com/Atitovva"}
            ep["space_url"] = "https://x.com/i/spaces/1OdKrXADwlXJX"
            ep["unlock_url"] = "https://app.unlock-protocol.com/event/banda-web-3-014-atitovva"
            ep["opensea_url"] = "https://opensea.io/collection/bandaweb3-015-atitovva"
            ep["contract_url"] = "https://arbiscan.io//address/0x8f4d86fd156a1fc32e9304612d94ea31fb922f95"
            ep["flyer_urls"] = ["../static/images/flyer_015.png"]
            ep["title"] = "Episode 015 with @Atitovva"
            ep["description"] = "Episode 015 of BandaWeb3 with special guest @Atitovva."
            updated_count += 1

    if updated_count > 0:
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print(f"Updated {updated_count} episodes (013, 014, 015).")
    else:
        print("Episodes 013, 014, 015 not found.")

if __name__ == "__main__":
    main()

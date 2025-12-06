import json
from pathlib import Path

# Extracted from CharmVerse (Browser Subagent)
charmverse_data = {
    "001": {"guests": ["0xKaroShow"]},
    "002": {"guests": ["sohobiit"]},
    "003": {"guests": ["sandym_c"]},
    "004": {"guests": ["natzcalli"]},
    "005": {"guests": ["haycarlitos"]},
    "006": {"guests": ["MinimalTrader_"]},
    "007": {"guests": ["Yisbelpd"]},
    "008": {"guests": ["jgonzalezferrer"]},
    "009": {"guests": ["VizZu11_11"]},
    "010": {"guests": ["andreweb3_btc"]},
    "011": {"guests": ["rosaglez_eth"]},
    "012": {"guests": ["asrvide9"]},
    "013": {"guests": ["AndriuJose20"]},
    "014": {"guests": ["AnanaNFTs"]},
    "015": {"guests": ["Atitovva"]},
    "016": {"guests": ["eddiespino"]},
    "017": {"guests": ["CryptoNotaz"]}
}

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)

    updated_count = 0
    
    for ep in db["episodes"]:
        ep_num = ep["number"]
        if ep_num in charmverse_data:
            # Update guests
            ep["guests"] = charmverse_data[ep_num]["guests"]
            # Set a slightly better title than "Pending Title" if strictly necessary, 
            # but user might prefer manual title edits later. 
            # For now, let's keep title as is or append guest name to title if it is "Pending Title"
            if ep["title"] == "Pending Title":
                ep["title"] = f"Episode {ep_num} with @{charmverse_data[ep_num]['guests'][0]}"
            
            updated_count += 1
            print(f"Updated Episode {ep_num}")

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully updated {updated_count} episodes from CharmVerse data.")

if __name__ == "__main__":
    main()

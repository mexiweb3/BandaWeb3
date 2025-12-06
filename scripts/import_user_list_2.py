import json
import re
from pathlib import Path
from datetime import datetime

def parse_date(date_str):
    try:
        # e.g. Jan 9 2024
        dt = datetime.strptime(date_str, "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
    
    existing_titles = {ep.get("title", ""): ep for ep in db["episodes"]}
    # Map normalized titles
    norm_titles = {}
    for t, ep in existing_titles.items():
        k = re.sub(r'\W+', '', t.lower())
        norm_titles[k] = ep

    txt_path = Path("website/inputs/hosted_spaces.txt")
    with open(txt_path, "r") as f:
        lines = f.readlines()
    
    new_eps = []
    
    # Parsing custom format:
    # 3-4 lines per item?
    # Line 1: Title (or metadata?)
    # Line 2: "es - Ended: ..."
    # Line 3..: Tags
    # Line N: Duration/Stats? 
    
    # Strategy: Iterate and look for "Ended:" line. The line before is Title.
    
    for i, line in enumerate(lines):
        if "Ended:" in line:
            # Found metadata line
            date_line = line.strip()
            
            # Title is likely i-1
            # But line i-1 might be "7k" or "@meximalist" or "meximalist"
            # It seems the block starts with "meximalist\nmexi\n@meximalist\n(maybe stats)\nTITLE"
            # Looking at the sample:
            # meximalist
            # mexi
            # @meximalist
            # 7k
            # AMA - ETF Bitcoin... (TITLE)
            # es - Ended: ...
            
            # So looking backwards from "Ended:", ignore shorter lines or specific keywords?
            # Let's iterate backwards from i-1
            title = "Unknown Title"
            for j in range(i-1, i-10, -1):
                if j < 0: break
                candidate = lines[j].strip()
                if not candidate: continue
                if candidate in ["meximalist", "mexi", "@meximalist", "7k"]: continue
                # Is it a number?
                if candidate.isdigit(): continue
                # Likely title
                title = candidate
                break
                
            # Parse Date/Duration
            # "es - Ended: Jan 9 2024 - Speakers: 5 - Duration: 2h 00m"
            date_str = ""
            duration = ""
            try:
                if "Ended:" in date_line:
                    parts = date_line.split("Ended:")[1].split("-")
                    date_str = parts[0].strip()
                    for p in parts:
                        if "Duration:" in p:
                            duration = p.split("Duration:")[1].strip()
            except:
                pass
            
            date_iso = parse_date(date_str)
            
            # Check existance
            t_norm = re.sub(r'\W+', '', title.lower())
            if t_norm in norm_titles:
                # print(f"Skipping existing: {title}")
                continue
            
            # Add new
            ep_num = date_iso.replace("-", "") if date_iso else "UNKNOWN"
            # Suffix if multiple on same day? handled by append order usually
            guests = re.findall(r"@(\w+)", title)
            guest_links = {g: f"https://x.com/{g}" for g in guests}

            new_ep = {
                "number": ep_num,
                "title": title,
                "date": date_iso,
                "duration": duration,
                "guests": guests,
                "guest_links": guest_links,
                "space_url": "", 
                "description": title,
                "topics": [],
                "status": "archived",
                "transcript_available": False,
                "content_generated": False,
                "flyer_urls": []
            }
            new_eps.append(new_ep)
            # Add to norm_titles to prevent duplicates within same batch
            norm_titles[t_norm] = new_ep

    print(f"Found {len(new_eps)} new 'Hosted Spaces' to add.")
    
    if new_eps:
        db["episodes"].extend(new_eps)
        # Sort
        def sort_key(ep):
            try:
                return datetime.strptime(ep["date"], "%Y-%m-%d")
            except:
                return datetime.min
        db["episodes"].sort(key=sort_key, reverse=True)
        
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Database updated with hosted spaces.")

if __name__ == "__main__":
    main()

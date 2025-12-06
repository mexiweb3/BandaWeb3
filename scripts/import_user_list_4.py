import json
import re
from pathlib import Path
from datetime import datetime

def parse_date(date_str):
    try:
        # e.g. Aug 1 2023
        dt = datetime.strptime(date_str, "%b %d %Y")
        return dt.strftime("%Y-%m-%d")
    except:
        return None

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
    
    existing_titles = {ep.get("title", ""): ep for ep in db["episodes"]}
    norm_titles = {}
    for t, ep in existing_titles.items():
        k = re.sub(r'\W+', '', t.lower())
        norm_titles[k] = ep

    txt_path = Path("website/inputs/hosted_spaces_3.txt")
    with open(txt_path, "r") as f:
        lines = f.readlines()
    
    new_eps = []
    
    for i, line in enumerate(lines):
        if "Ended:" in line:
            date_line = line.strip()
            
            # Find title
            title = "Unknown Host Space"
            for j in range(i-1, i-10, -1):
                if j < 0: break
                candidate = lines[j].strip()
                if not candidate: continue
                if candidate in ["meximalist", "mexi", "@meximalist", "7k", "Hosted Spaces"]: continue
                if candidate.isdigit(): continue
                title = candidate
                break
                
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
            
            t_norm = re.sub(r'\W+', '', title.lower())
            if t_norm in norm_titles:
                continue
            
            ep_num = date_iso.replace("-", "") if date_iso else "UNKNOWN"
            # Uniqueness check for same-day
            # If title is unique (checked above), we are good.
            
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
            norm_titles[t_norm] = new_ep

    print(f"Found {len(new_eps)} new 'Hosted Spaces' (Batch 3) to add.")
    
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
        print("Database updated with hosted spaces batch 3.")

if __name__ == "__main__":
    main()

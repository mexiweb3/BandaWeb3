import json
import re
from pathlib import Path
from datetime import datetime

# Logic:
# Parse co-hosted spaces.
# Detect Year:
# - Check explicit "2024", "2023", "2022".
# - If no year:
#   - If Month is Jan/Feb, assume 2025 (given context of "2025" in titles/metadata).
#   - If Month is Jul/Aug/Sep/Nov, assume 2024?
#     - "Ended: Nov 3" -> 2024 (Latam SZN)
#     - "Ended: Sep 11" -> 2024 (Women of Web3)
#     - "Ended: Jul 29" -> 2024 (Unlock Summit 2025 promo -> Jul 2024)
#     - "Ended: Feb 17" -> 2025 (Prep for EthDenver 2025)
#     - "Ended: Jan 27" -> 2025 (Narratives 2025)
#   - So: Jan-Feb -> 2025. Jul-Dec -> 2024.

def parse_smart_date(date_raw):
    # Try explicit year first
    years = re.findall(r"(20\d\d)", date_raw)
    if years:
        year = years[0]
        # remove year from string to parse month/day if needed, or just strptime
        try:
            # Try full format "MMM DD YYYY"
            dt = datetime.strptime(date_raw, "%b %d %Y")
            return dt.strftime("%Y-%m-%d")
        except:
             # Maybe "Nov 3 2024"?
             pass
             
    # No explicit year or failed parse
    # Guess year based on month
    # Clean date_raw "Nov 3" or "Sep 11"
    parts = date_raw.split()
    if len(parts) >= 2:
        month_str = parts[0]
        day_str = parts[1].replace(",", "")
        
        if month_str in ["Jan", "Feb", "Mar", "Apr", "May"]:
            year = "2025"
        else:
            year = "2024"
            
        full_str = f"{month_str} {day_str} {year}"
        try:
            dt = datetime.strptime(full_str, "%b %d %Y")
            return dt.strftime("%Y-%m-%d")
        except:
            pass
            
    return None

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
        
    existing_titles = {re.sub(r'\W+', '', ep.get("title", "").lower()): ep for ep in db["episodes"]}
    
    input_files = [
        "website/inputs/co_hosted_spaces.txt",
        "website/inputs/co_hosted_spaces_2.txt",
        "website/inputs/co_hosted_spaces_3.txt",
        "website/inputs/co_hosted_spaces_4.txt"
    ]
    
    lines = []
    for fname in input_files:
        p = Path(fname)
        if p.exists():
            with open(p, "r") as f:
                lines.extend(f.readlines())
                lines.append("\n") # Separator
        
    new_eps = []
    
    for i, line in enumerate(lines):
        if "Ended:" in line:
            date_line = line.strip()
            
            # Title is likely 2-3 lines up
            # Structure:
            # Handle
            # Name
            # Handle
            # Followers?
            # Title
            # Meta line (Ended: ...)
            
            title = "Unknown Co-Host Space"
            
            # Scan backwards for Title
            # Skip lines that are just numbers/Stats or Play/Replay or Hosts
            for j in range(i-1, i-6, -1):
                if j < 0: break
                candidate = lines[j].strip()
                if not candidate: continue
                if candidate == "PLAY" or candidate == "REPLAY": continue
                if candidate.isdigit() or "k" in candidate: continue # 2k, 7k
                if candidate.startswith("@"): continue
                
                # Check line before candidate?
                # Usually Title is the longest text block or specific format.
                # In provided:
                # @Musica_W3
                # 2k
                # Web3 en español 🚀 <- Title
                # es - Ended...
                
                title = candidate
                break
            
            # Date Parsing
            try:
                parts = date_line.split("Ended:")[1].split("-")
                date_raw = parts[0].strip() # "Sep 23 2024" or "Feb 17"
                date_iso = parse_smart_date(date_raw)
                
                duration = ""
                for p in parts:
                    if "Duration:" in p:
                        duration = p.split("Duration:")[1].strip()
            except:
                date_iso = None
                
            # Listeners
            listeners = ""
            # Look ahead
            for k in range(i+1, i+10):
                if k >= len(lines): break
                if "PLAY" in lines[k] or "REPLAY" in lines[k]:
                     # Line before
                     c = lines[k-1].strip()
                     if c.isdigit():
                         listeners = c
                     break
            
            t_norm = re.sub(r'\W+', '', title.lower())
            
            # Check duplicates
            if t_norm in existing_titles:
                # Update listeners?
                ep = existing_titles[t_norm]
                if listeners and not ep.get("listeners"):
                    ep["listeners"] = listeners
                continue
                
            # ID Gen
            base_id = date_iso.replace("-", "") if date_iso else f"COHOST_{i}"
            ep_num = base_id
            
            # Check for collision in new_eps
            collision_count = 1
            while any(e["number"] == ep_num for e in new_eps): # Slow but fine for small batch
                collision_count += 1
                ep_num = f"{base_id}-{collision_count}"
            
            # Also check existing DB (though unlikely to clash with main eps unless same numbering scheme used)
            # Main eps define 'number' as '074', '001' etc. Date-based IDs are used for these imports.
            # But wait, previous imports used similar scheme?
            # existing_titles keys are titles, not IDs.
            # We should probably check IDs in db["episodes"] but that variable is not in scope here efficiently?
            # 'db' variable is available.
            
            while any(e["number"] == ep_num for e in db["episodes"]):
                 collision_count += 1
                 ep_num = f"{base_id}-{collision_count}"
            
            guests = re.findall(r"@(\w+)", title)
            
            # Extract Host hint from previous lines?
            # Not critical but helpful description
            
            new_ep = {
                "number": ep_num,
                "title": title,
                "date": date_iso,
                "duration": duration,
                "guests": guests,
                "guest_links": {},
                "space_url": "", 
                "description": f"Co-hosted Space: {title}",
                "topics": [],
                "status": "archived",
                "transcript_available": False,
                "content_generated": False,
                "flyer_urls": [],
                "listeners": listeners
            }
            new_eps.append(new_ep)
            existing_titles[t_norm] = new_ep

    print(f"Found {len(new_eps)} new Co-Hosted Spaces.")
    
    if new_eps:
        db["episodes"].extend(new_eps)
        
        def sort_key(ep):
            try:
                return datetime.strptime(ep["date"], "%Y-%m-%d")
            except:
                return datetime.min
        db["episodes"].sort(key=sort_key, reverse=True)
        
        with open(db_path, "w") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)
        print("Database updated with co-hosted spaces.")

if __name__ == "__main__":
    main()

import json
import re
from pathlib import Path

def main():
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
        
    # Create lookup map for episodes: normalized title -> episode object
    # AND title -> episode object
    ep_map = {}
    for ep in db["episodes"]:
        t_norm = re.sub(r'\W+', '', ep.get("title", "").lower())
        ep_map[t_norm] = ep
    
    files_to_check = [
        "website/inputs/user_text_list.txt",
        "website/inputs/hosted_spaces.txt",
        "website/inputs/hosted_spaces_2.txt",
        "website/inputs/hosted_spaces_3.txt",
        "website/inputs/hosted_spaces_4.txt",
        "website/inputs/hosted_spaces_5.txt",
        "website/inputs/hosted_spaces_6.txt",
        "website/inputs/co_hosted_spaces.txt",
        "website/inputs/co_hosted_spaces_2.txt",
        "website/inputs/co_hosted_spaces_3.txt",
        "website/inputs/co_hosted_spaces_4.txt"
    ]
    
    updates = 0
    
    for fname in files_to_check:
        path = Path(fname)
        if not path.exists():
            continue
            
        with open(path, "r") as f:
            lines = f.readlines()
            
        # Strategy: Look for "PLAY" or "REPLAY". The line BEFORE it usually contains the number.
        # Or, the line containing PLAY/REPLAY might have the number if stuck together.
        # In the provided examples:
        # "244 \n REPLAY"
        # or sometimes "304 \n REPLAY"
        
        for i, line in enumerate(lines):
            if "REPLAY" in line or "PLAY" in line:
                # Look for number in previous lines
                listeners = None
                
                # Check current line first (just in case "244 REPLAY")
                current_nums = re.findall(r"(\d+)\s*(?:REPLAY|PLAY)", line)
                if current_nums:
                     listeners = current_nums[0]
                
                if not listeners and i > 0:
                    # Check i-1
                    prev = lines[i-1].strip()
                    if prev.isdigit():
                        listeners = prev
                    else:
                        # Sometimes it might be "244 \t REPLAY" or similar on same line?
                        # Or maybe i-2?
                        pass
                
                if listeners:
                    # Now find WHICH episode this belongs to.
                    # We need to look UPWARDS from here to find the "Ended:" line, then Title.
                    
                    found_title = None
                    for j in range(i-1, i-20, -1):
                        if j < 0: break
                        l = lines[j].strip()
                        if "Ended:" in l:
                            # Found date line. Title is usually before this.
                            # Look back from date line for title
                            for k in range(j-1, j-10, -1):
                                if k < 0: break
                                lb = lines[k].strip()
                                if not lb: continue
                                if lb in ["meximalist", "mexi", "@meximalist", "7k", "Hosted Spaces"]: continue
                                if lb.isdigit(): continue
                                found_title = lb
                                break
                            break
                    
                    if found_title:
                        # Normalize and match
                        t_norm = re.sub(r'\W+', '', found_title.lower())
                        if t_norm in ep_map:
                            ep = ep_map[t_norm]
                            old_l = ep.get("listeners")
                            if old_l != listeners:
                                ep["listeners"] = listeners
                                updates += 1
                                # print(f"Updated listeners for '{found_title}': {listeners}")

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
        
    print(f"Updated listener counts for {updates} episodes.")

if __name__ == "__main__":
    main()

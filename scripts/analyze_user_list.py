import json
import re
from pathlib import Path

def main():
    # Load DB
    db_path = Path("data/episodes_database.json")
    with open(db_path, "r") as f:
        db = json.load(f)
    
    existing_nums = {ep["number"] for ep in db["episodes"]}
    
    # helper to find ep by number
    def get_ep(num):
        for ep in db["episodes"]:
            if ep["number"] == num:
                return ep
        return None

    # Load User Text
    txt_path = Path("website/inputs/user_text_list.txt")
    with open(txt_path, "r") as f:
        lines = f.readlines()
    
    print("--- Analysis of Provided Text ---")
    
    # Parse text blocks
    # We look for lines containing "BandaWeb3 #XXX" or just titles
    
    found_in_text = []
    
    # Iterate lines
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check for Numbered Episodes
        match = re.search(r"BandaWeb3 #(\d+)", line)
        if match:
            num = match.group(1)
            title = line
            # Try to find date in next few lines
            date_str = "Unknown"
            if i + 1 < len(lines) and "Ended:" in lines[i+1]:
                date_str = lines[i+1].split("Ended:")[1].split("-")[0].strip()
            
            found_in_text.append({"num": num, "title": title, "date": date_str})
            continue
            
        # Check for unnumbered special ones if needed, but user seems focused on the numbered list
        if "100K TODAY" in line:
             found_in_text.append({"num": "N/A", "title": "100K TODAY", "date": "Dec 5 2024"})
    
    # Analyze
    seen_nums = {} # check for duplicates in user list
    
    for item in found_in_text:
        num = item["num"]
        title = item["title"]
        date = item["date"]
        
        if num != "N/A":
            if num in seen_nums:
                print(f"[CONFLICT IN LIST] Episode #{num} appears multiple times in your list:")
                print(f"  1. {seen_nums[num]['title']}")
                print(f"  2. {title}")
            seen_nums[num] = item
            
            # Check against DB
            if num in existing_nums:
                # print(f"[EXISTING] #{num} already in DB.")
                pass
            else:
                print(f"[MISSING IN DB] #{num} - {title} ({date}) is NOT in your database.")
        else:
             print(f"[NOTE] Unnumbered Space: '{title}' ({date}) found.")

    print("\n--- Summary ---")
    print(f"Total numbered episodes in user list: {len(seen_nums)}")
    missing_count = 0
    for num in seen_nums:
        if num not in existing_nums:
            missing_count += 1
    print(f"Episodes from this list missing in DB: {missing_count}")

if __name__ == "__main__":
    main()

import os
import json
import shutil
from pathlib import Path
from difflib import SequenceMatcher

TRANSCRIPTS_DIR = Path("shared/transcriptions_fireflies")
DB_PATH = Path("shared/episodes_database.json")

def load_database():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def clean_title(title):
    # Remove common prefixes/suffixes added by Fireflies or file naming
    t = title.lower()
    t = t.replace("bandaweb3 - ", "").replace("bandaweb3 #", "")
    t = t.replace(".mp3", "").strip()
    return t

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def main():
    db = load_database()
    episodes = db.get("episodes", [])
    
    # Filter files that look like Fireflies IDs (starts with 01)
    files_to_fix = [f for f in os.listdir(TRANSCRIPTS_DIR) 
                    if f.endswith("_fireflies.json") and f.startswith("01")]
    
    print(f"Found {len(files_to_fix)} files to process")
    
    renamed_count = 0
    
    for filename in files_to_fix:
        filepath = TRANSCRIPTS_DIR / filename
        
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        ft_title = data.get("title", "")
        cleaned_ft_title = clean_title(ft_title)
        
        # Try to find match in DB
        best_match = None
        best_score = 0
        
        for ep in episodes:
            # Check title match
            ep_title = ep.get("title", "")
            cleaned_ep_title = clean_title(ep_title)
            
            score = similarity(cleaned_ft_title, cleaned_ep_title)
            
            # Check if title contains the space ID (sometimes Fireflies titling is weird)
            space_url = ep.get("space_url", "")
            space_id = space_url.split("/")[-1] if space_url else ""
            
            if space_id and space_id in ft_title:
                score = 1.0 # Perfect match via ID in title
            
            if score > best_score:
                best_score = score
                best_match = ep
        
        if best_match and best_score > 0.6: # Threshold for reasonable match
            space_url = best_match.get("space_url", "")
            if not space_url:
                print(f"❌ Match found but no space_url for: {ft_title}")
                continue
                
            space_id = space_url.split("/")[-1].split("?")[0]
            if not space_id:
                continue

            new_json_name = f"{space_id}_fireflies.json"
            new_txt_name = f"{space_id}_fireflies.txt"
            
            print(f"✅ Match: '{ft_title}' -> '{best_match['title']}' (Score: {best_score:.2f})")
            print(f"   Renaming to: {new_json_name}")
            
            # Rename JSON
            os.rename(filepath, TRANSCRIPTS_DIR / new_json_name)
            
            # Rename TXT if exists
            txt_filename = filename.replace(".json", ".txt")
            txt_filepath = TRANSCRIPTS_DIR / txt_filename
            if txt_filepath.exists():
                os.rename(txt_filepath, TRANSCRIPTS_DIR / new_txt_name)
            
            renamed_count += 1
        else:
            print(f"⚠️  No good match for: '{ft_title}' (Best score: {best_score:.2f})")

    print(f"\nRenamed {renamed_count} files.")

if __name__ == "__main__":
    main()

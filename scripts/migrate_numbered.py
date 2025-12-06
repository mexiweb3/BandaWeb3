import json
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'shared', 'episodes_database.json')

def migrate_numbered():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    episodes = data.get('episodes', [])
    updated_count = 0

    for ep in episodes:
        num = str(ep.get('number', ''))
        
        # Criteria: numeric string, length <= 3 (e.g. "001", "074", "1", "99")
        # AND not already co-hosted (though user request didn't specify exclusion, 
        # usually numbered are the main ones).
        # User manual request: "numerados de 001 a 074".
        
        is_numbered = False
        if num.isdigit() and len(num) <= 3:
             is_numbered = True
             
        if is_numbered:
            # Check for conflict? User said "add a field".
            # If it's already co-hosted, it shouldn't overwrite unless we support multiple types.
            # But earlier standard was "digit <= 3" implies hosted.
            # Now we explicitly want to mark them.
            
            # If currently has NO type, set it to "numbered".
            # If it says "co-hosted", we probably shouldn't change it to "numbered" unless user resolves ambiguity.
            # However, looking at data, numbered ones like 074 seem to be main episodes.
            
            if ep.get('type') == 'co-hosted':
                print(f"Skipping Co-Hosted: #{num} - {ep['title']}")
                continue
                
            if ep.get('type') != 'numbered':
                ep['type'] = 'numbered'
                updated_count += 1
                print(f"Marked as Numbered: #{num} - {ep['title']}")

    if updated_count > 0:
        data['episodes'] = episodes
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully marked {updated_count} episodes as numbered.")
    else:
        print("\nNo new episodes matched criteria.")

if __name__ == "__main__":
    migrate_numbered()

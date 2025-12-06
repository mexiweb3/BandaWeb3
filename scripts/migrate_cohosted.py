import json
import os
import re

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'shared', 'episodes_database.json')

def migrate_cohosted():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    episodes = data.get('episodes', [])
    updated_count = 0

    for ep in episodes:
        description = ep.get('description', '')
        title = ep.get('title', '')
        
        # Check for case-insensitive "co-hosted" or "cohosted"
        is_cohosted = False
        if re.search(r"co-?hosted", description, re.IGNORECASE):
            is_cohosted = True
        elif re.search(r"co-?hosted", title, re.IGNORECASE):
            is_cohosted = True
            
        if is_cohosted:
            # Only update if not already marked (or enforce it)
            if ep.get('type') != 'co-hosted':
                ep['type'] = 'co-hosted'
                updated_count += 1
                print(f"Marked as Co-Hosted: #{ep['number']} - {ep['title']}")
        elif ep.get('type') == 'co-hosted':
            # Option to clear it if it doesn't match criteria? 
            # Better to be safe and only ADD the tag, not remove it unless we are sure.
            # But the requirement is to add it where it 'says' co-hosted.
            pass

    if updated_count > 0:
        data['episodes'] = episodes
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully marked {updated_count} episodes as co-hosted.")
    else:
        print("\nNo new episodes matched criteria.")

if __name__ == "__main__":
    migrate_cohosted()

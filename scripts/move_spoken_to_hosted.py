
import json
import os
from datetime import datetime

EPISODES_DB_PATH = 'shared/episodes_database.json'
SPOKEN_DB_PATH = 'shared/spoken_database.json'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("🔄 Moving episodes from Spoken to Episodes DB...")
    
    episodes_db = load_json(EPISODES_DB_PATH)
    spoken_db = load_json(SPOKEN_DB_PATH)
    
    ids_to_move = [
        "1YpKkwjrPVrKj",
        "1jMJgBmZDpMGL",
        "1vOxwdpjNDDKB",
        "1ZkJzZEjPbwJv",
        "1MnxnpyabeyGO"
    ]
    
    moved_count = 0
    remaining_spoken = []
    
    for ep in spoken_db['episodes']:
        # Extract ID from space_url if id field missing
        ep_id = ep.get('id')
        if not ep_id and ep.get('space_url'):
            ep_id = ep['space_url'].split('/')[-1].split('?')[0]
            
        if ep_id in ids_to_move:
            print(f"📦 Moving: {ep.get('title', 'Unknown Title')} ({ep_id})")
            
            # Prepare for Episodes DB
            # Use 'co-hosted' type if unsure, or defaults
            # Most spoken episodes have detailed metadata already
            new_ep = ep.copy()
            new_ep['type'] = 'co-hosted' # Assume co-hosted if moving from spoken
            new_ep['transcript_available'] = True # We have the transcripts
            
            # Ensure number field exists (use date or ID if missing)
            if 'number' not in new_ep:
                new_ep['number'] = ep_id
                
            # Add to Episodes DB
            episodes_db['episodes'].append(new_ep)
            moved_count += 1
        else:
            remaining_spoken.append(ep)
            
    # Update Spoken DB (remove moved)
    spoken_db['episodes'] = remaining_spoken
    
    # Sort Episodes DB
    episodes_db['episodes'].sort(key=lambda x: x.get('date', ''), reverse=True)
    
    if moved_count > 0:
        save_json(EPISODES_DB_PATH, episodes_db)
        save_json(SPOKEN_DB_PATH, spoken_db)
        print(f"✅ Successfully moved {moved_count} episodes to episodes_database.json")
    else:
        print("⚠️ No episodes found to move")

if __name__ == "__main__":
    main()

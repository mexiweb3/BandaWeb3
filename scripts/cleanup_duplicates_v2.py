
import json
import os

DB_PATH = 'shared/episodes_database.json'
SPOKEN_PATH = 'shared/spoken_database.json'
AUDIO_DIR = 'shared/audio'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("🧹 Cleaning up duplicates...")
    db = load_json(DB_PATH)
    
    # IDs of the 7 "new" episodes to remove
    ids_to_remove = [
        "1yoJMPVEEzeGQ",
        "1YpKkwjrPVrKj",
        "1jMJgBmZDpMGL",
        "1MnGnPewjVjxO",
        "1vOxwdpjNDDKB",
        "1ZkJzZEjPbwJv",
        "1MnxnpyabeyGO"
    ]
    
    # 1. Update existing valid episodes
    # #075 -> 1yoJMPVEEzeGQ
    # #074 -> 1MnGnPewjVjxO
    
    for ep in db['episodes']:
        # Check #075
        if ep.get('number') == '075':
            print("✅ Updating #075 (1yoJMPVEEzeGQ) transcript status")
            ep['transcript_available'] = True
            
        # Check #074
        if ep.get('number') == '074':
            print("✅ Updating #074 (1MnGnPewjVjxO) transcript status")
            ep['transcript_available'] = True
            
        # Check by Space ID in URL for others
        # (The other 5 might be in Spoken DB, not here)
        
    # 2. Remove the generic entries
    original_count = len(db['episodes'])
    db['episodes'] = [ep for ep in db['episodes'] if ep.get('id') not in ids_to_remove or ep.get('title') != f"Twitter Space {ep.get('id')}"]
    new_count = len(db['episodes'])
    
    print(f"🗑️ Removed {original_count - new_count} duplicate entries")
    
    # 3. Check Spoken DB for the other 5 and update if needed
    # For now, just logging where they are
    
    save_json(DB_PATH, db)
    print("💾 Database saved")

if __name__ == "__main__":
    main()

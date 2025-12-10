
import json

EPISODES_DB_PATH = 'shared/episodes_database.json'
SPOKEN_DB_PATH = 'shared/spoken_database.json'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("🔄 Reverting 5 episodes from Episodes DB back to Spoken DB...")
    
    episodes_db = load_json(EPISODES_DB_PATH)
    spoken_db = load_json(SPOKEN_DB_PATH)
    
    ids_to_revert = [
        "1ZkJzZEjPbwJv",
        "1vOxwdpjNDDKB",
        "1jMJgBmZDpMGL",
        "1YpKkwjrPVrKj",
        "1MnxnpyabeyGO"
    ]
    
    reverted_count = 0
    remaining_episodes = []
    
    for ep in episodes_db['episodes']:
        ep_id = ep.get('id')
        if not ep_id and ep.get('space_url'):
             ep_id = ep['space_url'].split('/')[-1].split('?')[0]
             
        if ep_id in ids_to_revert:
            print(f"📦 Reverting: {ep.get('title', 'Unknown Title')} ({ep_id})")
            
            # Prepare for Spoken DB
            # We restore them basically as they were, but keep transcript info if possible??
            # Spoken DB schema is simpler. Let's look at existing entries.
            # They have 'type': 'Spoken', 'title', 'host', 'listeners', 'date', 'speakers', 'duration', 'space_url', 'spacesdashboard_url', 'number'
            
            # Since I didn't save a backup of the EXACT state before move, I have to reconstruct or merge.
            # Thankfully, I just moved them, so the data in 'ep' is good.
            # BUT, the original spoken DB had specific fields.
            # The 'move_spoken_to_hosted.py' COPIED them and added fields.
            # So 'ep' has all the spoken fields PLUS new ones.
            # I can just push 'ep' back to spoken_db['episodes'], 
            # maybe setting 'type' back to 'Spoken'.
            
            reverted_ep = ep.copy()
            reverted_ep['type'] = 'Spoken'
            
            # Remove hosted-specific fields if they clutter Spoken DB?
            # Spoken DB seems flexible. Let's keep extra info (transcript_available etc) as a bonus.
            
            spoken_db['episodes'].append(reverted_ep)
            reverted_count += 1
        else:
            remaining_episodes.append(ep)
            
    # Update Episodes DB
    episodes_db['episodes'] = remaining_episodes
    
    # Sort Spoken DB
    spoken_db['episodes'].sort(key=lambda x: x.get('date', ''), reverse=True)
    
    if reverted_count > 0:
        save_json(EPISODES_DB_PATH, episodes_db)
        save_json(SPOKEN_DB_PATH, spoken_db)
        print(f"✅ Successfully reverted {reverted_count} episodes back to spoken_database.json")
    else:
        print("⚠️ No episodes found to revert")

if __name__ == "__main__":
    main()

import json
from pathlib import Path

# Paths
SHARED_DIR = Path('shared')
SPOKEN_DB_PATH = SHARED_DIR / 'spoken_database.json'

def sort_database():
    if not SPOKEN_DB_PATH.exists():
        print(f"Error: Database not found at {SPOKEN_DB_PATH}")
        return

    try:
        with open(SPOKEN_DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'episodes' not in data:
             print("Error: 'episodes' key not found in database.")
             return

        episodes = data['episodes']
        print(f"Loaded {len(episodes)} episodes.")
        
        # Sort by date descending (newest first)
        sorted_episodes = sorted(episodes, key=lambda x: x.get('date', ''), reverse=True)
        data['episodes'] = sorted_episodes
        
        with open(SPOKEN_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print("Database successfully sorted by date (descending).")
        
        # Verify first few dates
        print("Top 5 episodes after sorting:")
        for ep in sorted_episodes[:5]:
            print(f"- {ep.get('date')} : {ep.get('title')}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    sort_database()

import json
from pathlib import Path

def check_db(path):
    print(f"Checking {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        episodes = data.get('episodes', [])
        print(f"Type of 'episodes': {type(episodes)}")
        if episodes is None:
            print("ALERT: 'episodes' is None!")
        elif isinstance(episodes, list):
            print(f"Count: {len(episodes)}")
        else:
            print(f"Unexpected type: {type(episodes)}")
            
    except Exception as e:
        print(f"Error: {e}")

check_db("shared/episodes_database.json")
check_db("shared/consolidated_database.json")

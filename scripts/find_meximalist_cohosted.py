import json

def search_episodes():
    try:
        with open('shared/episodes_database.json', 'r') as f:
            data = json.load(f)
            
        episodes = data.get('episodes', [])
        print(f"Total episodes in database: {len(episodes)}")
        
        matches = []
        for ep in episodes:
            if ep.get('type') != 'co-hosted':
                continue
                
            title = ep.get('title', '')
            # Check if 'meximalist' is in title (case insensitive)
            if 'meximalist' in title.lower():
                matches.append(ep)
        
        print(f"\nFound {len(matches)} co-hosted episodes with 'meximalist' in the title:\n")
        
        # Sort by date descending
        matches.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        for ep in matches:
            date = ep.get('date', 'N/A')
            title = ep.get('title', 'N/A')
            url = ep.get('space_url', 'N/A')
            print(f"[{date}] {title}")
            print(f"   URL: {url}")
            print("-" * 50)
            
    except FileNotFoundError:
        print("Error: shared/episodes_database.json not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")

if __name__ == "__main__":
    search_episodes()

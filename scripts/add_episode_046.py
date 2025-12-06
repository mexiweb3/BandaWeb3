import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'shared', 'episodes_database.json')

def add_episode_046():
    with open(DB_PATH, 'r') as f:
        data = json.load(f)

    episodes = data.get('episodes', [])
    
    # Check if 046 already exists (safety check)
    if any(ep['number'] == '046' for ep in episodes):
        print("Episode 046 already exists. Skipping.")
        return

    new_episode = {
      "number": "046",
      "title": "BandaWeb3 #046 (Placeholder)",
      "date": "2025-03-20",
      "time": "12:00 PM CST",
      "duration": "",
      "guests": [],
      "guest_links": {},
      "space_url": "",
      "description": "BandaWeb3 #046 (Recovered from flyer). Metadata pending.",
      "topics": [],
      "status": "archived",
      "transcript_available": False,
      "content_generated": False,
      "flyer_urls": [
        "flyer_046.png"
      ],
      "listeners": "0"
    }
    
    # Needs Python boolean for json dump? No, json load makes them Py bools.
    # In the dict literal above: false -> False
    new_episode['transcript_available'] = False
    new_episode['content_generated'] = False

    episodes.append(new_episode)
    
    # Sort by number descending (assuming that's the order, or date)
    # The file seems to be roughly descending order.
    # Let's sort by date descending to be safe.
    episodes.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    data['episodes'] = episodes

    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Added Episode 046 and saved database.")

if __name__ == "__main__":
    add_episode_046()

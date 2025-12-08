import json
from pathlib import Path
from difflib import SequenceMatcher

SHARED_DIR = Path('shared')
SPOKEN_DB_PATH = SHARED_DIR / 'spoken_database.json'
EPISODES_DB_PATH = SHARED_DIR / 'episodes_database.json'

def normalize(s):
    return ''.join(c.lower() for c in str(s) if c.isalnum())

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def check_overlap():
    if not SPOKEN_DB_PATH.exists() or not EPISODES_DB_PATH.exists():
        print("Error: One or both database files missing.")
        return

    with open(SPOKEN_DB_PATH, 'r', encoding='utf-8') as f:
        spoken_data = json.load(f)
        # Handle recent structural change where episodes are in 'episodes' key
        if isinstance(spoken_data, dict) and 'episodes' in spoken_data:
            spoken_eps = spoken_data['episodes']
        else:
            spoken_eps = spoken_data

    with open(EPISODES_DB_PATH, 'r', encoding='utf-8') as f:
        all_eps = json.load(f)

    cohosted_eps = [ep for ep in all_eps if ep.get('type') == 'co-hosted']

    print(f"Loaded {len(spoken_eps)} Spoken episodes.")
    print(f"Loaded {len(cohosted_eps)} Co-hosted episodes (from {len(all_eps)} total in main DB).")
    print("-" * 60)

    matches = []

    # Map Space URLs to Spoken episodes for fast lookup
    spoken_urls = {}
    for ep in spoken_eps:
        url = ep.get('space_url')
        if url:
            # simple normalization of URL: strip trailing slash
            url = url.strip().rstrip('/')
            spoken_urls[url] = ep

    for ch_ep in cohosted_eps:
        match_found = False
        
        # 1. Check Space URL
        ch_url = ch_ep.get('space_url')
        if ch_url:
            ch_url = ch_url.strip().rstrip('/')
            if ch_url in spoken_urls:
                matches.append({
                    'reason': 'Space URL Match',
                    'cohosted': ch_ep,
                    'spoken': spoken_urls[ch_url]
                })
                match_found = True

        # 2. If no URL match, check Title Fuzzy Match
        if not match_found:
            ch_title = ch_ep.get('title', '')
            for sp_ep in spoken_eps:
                sp_title = sp_ep.get('title', '')
                
                # High threshold for fuzzy match
                ratio = similar(ch_title, sp_title)
                if ratio > 0.85: # 85% similarity
                     matches.append({
                        'reason': f'Title Match ({ratio:.2f})',
                        'cohosted': ch_ep,
                        'spoken': sp_ep
                    })
                     break

    if not matches:
        print("No overlaps found between Spoken and Co-hosted episodes.")
    else:
        print(f"Found {len(matches)} potential overlaps:\n")
        for m in matches:
            print(f"[{m['reason']}]")
            print(f"  Co-hosted: {m['cohosted'].get('title')} ({m['cohosted'].get('date')})")
            print(f"  Spoken:    {m['spoken'].get('title')} ({m['spoken'].get('date')})")
            print("-" * 40)

if __name__ == "__main__":
    check_overlap()

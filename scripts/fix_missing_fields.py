
import json

DB_PATH = 'shared/episodes_database.json'

def main():
    print("🔧 Fixing missing fields in database...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    fixed_count = 0
    for ep in data['episodes']:
        changed = False
        
        if 'description' not in ep:
            ep['description'] = ""
            changed = True
            
        if 'topics' not in ep:
            ep['topics'] = []
            changed = True
            
        if 'guests' not in ep:
            ep['guests'] = []
            changed = True
            
        if 'flyer_urls' not in ep:
            ep['flyer_urls'] = []
            changed = True
            
        if 'links' not in ep:
            ep['links'] = {}
            changed = True
            
        if changed:
            fixed_count += 1
            print(f"   Fixed: {ep.get('title', 'Unknown')}")
            
    if fixed_count > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Fixed {fixed_count} episodes with missing fields.")
    else:
        print("✅ No missing fields found.")

if __name__ == "__main__":
    main()

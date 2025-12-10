
import json

DB_PATH = 'shared/episodes_database.json'

def main():
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    fixed_count = 0
    for ep in data['episodes']:
        if 'description' not in ep:
            print(f"⚠️ Missing description for episode: {ep.get('title', 'Unknown')}")
            ep['description'] = ""
            fixed_count += 1
            
    if fixed_count > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Fixed {fixed_count} episodes with missing description.")
    else:
        print("✅ No missing descriptions found.")

if __name__ == "__main__":
    main()

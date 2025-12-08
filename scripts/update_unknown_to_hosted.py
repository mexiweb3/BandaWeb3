import json

db_path = 'shared/episodes_database.json'

with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for ep in data['episodes']:
    t = ep.get('type')
    if not t or t == 'unknown':
        ep['type'] = 'hosted'
        count += 1
        print(f"Updated: {ep.get('title')}")

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Successfully updated {count} episodes to 'hosted'.")

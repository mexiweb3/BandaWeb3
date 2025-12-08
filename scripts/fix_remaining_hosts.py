import json

db_path = 'shared/episodes_database.json'

with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for ep in data['episodes']:
    title = ep.get('title', '')
    date = ep.get('date', '')
    
    # 1. THREADS vs Twitter (2023-07-06)
    if 'THREADS vs Twitter' in title and date == '2023-07-06':
        ep['host'] = '@ElMcBoBo'
        count += 1
        print(f"Updated host for {title}")

    # 2. El Profesor - Danny Sánchez (2022-11-28)
    if 'El Profesor - Danny Sánchez' in title and date == '2022-11-28':
        ep['host'] = '@El_Profesor_eth'
        count += 1
        print(f"Updated host for {title}")

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Manually updated {count} episodes.")

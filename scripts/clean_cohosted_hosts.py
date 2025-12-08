import json

db_path = 'shared/episodes_database.json'

corrections = {
    'Ethereum Mexico 🇲🇽': '@ethereum_mexico',
    'cryptoreuMD.eth/3972.⌐◨-◨ 🦇🔊...': '@cryptoreumd',
    'McBoBo': '@TortillasTown',
    'THREADS vs Twitter: La Atencion te va hacer billonario$$$📈': '@ElMcBoBo',
    'THREADS vs Twitter: La Atencion te va hacer billonario$$$': '@ElMcBoBo',
    'Felipe Servin ⚡️': '@fservin',
    'TATO': '@NFTDEFILAND',
    'El Profesor - Danny Sánchez': '@El_Profesor_eth',
    'Diego Benítez Concha': '@diegobc28'
}

with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for ep in data['episodes']:
    title = ep.get('title')
    if title in corrections:
        old_host = ep.get('host')
        new_host = corrections[title]
        # Only update if different to avoid noise, but user provided explicit list
        # so let's enforce it.
        if old_host != new_host:
            ep['host'] = new_host
            count += 1
            print(f"Updated host for '{title}': {old_host} -> {new_host}")

with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Cleaned {count} host handles.")

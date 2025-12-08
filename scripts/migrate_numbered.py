#!/usr/bin/env python3
"""
Migrate numbered episodes from type="numbered" to type="hosted" + is_numbered=true
"""
import json

def migrate():
    path = 'shared/episodes_database.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    episodes = data.get('episodes', [])
    count = 0
    
    for ep in episodes:
        if ep.get('type') == 'numbered':
            ep['type'] = 'hosted'
            ep['is_numbered'] = True
            if not ep.get('host'):
                ep['host'] = 'BandaWeb3'
            count += 1
            print(f"Migrated: {ep.get('title')}")
            
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSuccessfully migrated {count} episodes.")

if __name__ == '__main__':
    migrate()

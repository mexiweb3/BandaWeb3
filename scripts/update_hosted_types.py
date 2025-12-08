#!/usr/bin/env python3
"""
Script to update all episodes with host @meximalist or BandaWeb3 to have type: "hosted"
"""
import json

def update_hosted_types():
    # Load the database
    with open('shared/episodes_database.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    episodes = data.get('episodes', [])
    updated_count = 0
    
    for episode in episodes:
        host = episode.get('host', '')
        current_type = episode.get('type', '')
        
        # If host is @meximalist or BandaWeb3, set type to "hosted"
        if host in ['@meximalist', 'BandaWeb3']:
            if current_type != 'hosted':
                episode['type'] = 'hosted'
                updated_count += 1
                print(f"Updated episode: {episode.get('title', 'Unknown')} - Old type: '{current_type}' -> New type: 'hosted'")
    
    # Save the updated database
    with open('shared/episodes_database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Total episodes updated: {updated_count}")
    
    # Show summary
    type_counts = {}
    host_counts = {}
    
    for ep in episodes:
        ep_type = ep.get('type', 'sin tipo')
        ep_host = ep.get('host', 'sin host')
        
        type_counts[ep_type] = type_counts.get(ep_type, 0) + 1
        host_counts[ep_host] = host_counts.get(ep_host, 0) + 1
    
    print('\n=== RESUMEN DESPUÉS DE LA ACTUALIZACIÓN ===')
    print('\nTipos:')
    for t, count in sorted(type_counts.items()):
        print(f'  {t}: {count} episodios')
    
    print('\nHosts:')
    for h, count in sorted(host_counts.items()):
        print(f'  {h}: {count} episodios')

if __name__ == '__main__':
    update_hosted_types()

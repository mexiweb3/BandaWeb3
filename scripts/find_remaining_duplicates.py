#!/usr/bin/env python3
"""
Script para encontrar los duplicados restantes entre episodes_database.json y spoken_database.json
"""

import json
from pathlib import Path

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_remaining_duplicates():
    """Encuentra duplicados restantes entre las dos bases de datos"""
    
    print("\n" + "="*100)
    print("BUSCANDO DUPLICADOS RESTANTES")
    print("="*100 + "\n")
    
    # Cargar ambas bases de datos
    episodes_db = load_json('shared/episodes_database.json')
    spoken_db = load_json('shared/spoken_database.json')
    
    episodes_list = episodes_db.get('episodes', [])
    spoken_list = spoken_db.get('episodes', [])
    
    print(f"📊 Episodios en episodes_database.json: {len(episodes_list)}")
    print(f"📊 Episodios en spoken_database.json: {len(spoken_list)}")
    print(f"📊 Suma total: {len(episodes_list) + len(spoken_list)}")
    
    # Buscar duplicados por space_url
    duplicates = []
    
    for episode in episodes_list:
        space_url = episode.get('space_url', '')
        if not space_url:
            continue
            
        for spoken in spoken_list:
            spoken_url = spoken.get('space_url', '')
            if spoken_url and space_url == spoken_url:
                duplicates.append({
                    'space_url': space_url,
                    'title_episodes': episode.get('title', 'N/A'),
                    'title_spoken': spoken.get('title', 'N/A'),
                    'date_episodes': episode.get('date', 'N/A'),
                    'date_spoken': spoken.get('date', 'N/A'),
                    'number_episodes': episode.get('number', 'N/A'),
                    'number_spoken': spoken.get('number', 'N/A'),
                    'host_episodes': episode.get('host', 'N/A'),
                    'host_spoken': spoken.get('host', 'N/A'),
                })
                break
    
    print(f"\n❌ Duplicados encontrados: {len(duplicates)}\n")
    
    if duplicates:
        print(f"{'='*100}")
        print("LISTA DE DUPLICADOS RESTANTES:")
        print(f"{'='*100}\n")
        
        for i, dup in enumerate(duplicates, 1):
            print(f"{i}. {dup['title_episodes']}")
            print(f"   Fecha: {dup['date_episodes']} | Host: {dup['host_episodes']}")
            print(f"   Space URL: {dup['space_url']}")
            print(f"   Number en episodes: {dup['number_episodes']} | Number en spoken: {dup['number_spoken']}\n")
    else:
        print("✅ No se encontraron duplicados restantes.\n")
    
    print(f"{'='*100}\n")
    
    # Guardar reporte
    report = {
        'total_duplicates': len(duplicates),
        'duplicates': duplicates
    }
    
    with open('shared/remaining_duplicates_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Reporte guardado en: shared/remaining_duplicates_report.json\n")
    
    return duplicates

if __name__ == '__main__':
    find_remaining_duplicates()

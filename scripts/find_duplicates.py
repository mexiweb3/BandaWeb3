#!/usr/bin/env python3
"""
Script para identificar episodios duplicados entre episodes_database.json y spoken_database.json
"""

import json
from pathlib import Path

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_duplicates():
    """Encuentra episodios duplicados entre las dos bases de datos"""
    
    # Cargar ambas bases de datos
    episodes_db = load_json('shared/episodes_database.json')
    spoken_db = load_json('shared/spoken_database.json')
    
    episodes_list = episodes_db.get('episodes', [])
    spoken_list = spoken_db.get('episodes', [])
    
    duplicates = []
    
    # Comparar por space_url (el identificador más confiable)
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
                    'listeners_episodes': episode.get('listeners', 'N/A'),
                    'listeners_spoken': spoken.get('listeners', 'N/A'),
                    'host_episodes': episode.get('host', 'N/A'),
                    'host_spoken': spoken.get('host', 'N/A'),
                })
                break
    
    # Imprimir resultados
    print(f"\n{'='*100}")
    print(f"EPISODIOS DUPLICADOS ENCONTRADOS: {len(duplicates)}")
    print(f"{'='*100}\n")
    
    if duplicates:
        for i, dup in enumerate(duplicates, 1):
            print(f"\n{'-'*100}")
            print(f"DUPLICADO #{i}")
            print(f"{'-'*100}")
            print(f"Space URL: {dup['space_url']}")
            print(f"\nEn episodes_database.json:")
            print(f"  - Número: {dup['number_episodes']}")
            print(f"  - Título: {dup['title_episodes']}")
            print(f"  - Fecha: {dup['date_episodes']}")
            print(f"  - Host: {dup['host_episodes']}")
            print(f"  - Listeners: {dup['listeners_episodes']}")
            print(f"\nEn spoken_database.json:")
            print(f"  - Número: {dup['number_spoken']}")
            print(f"  - Título: {dup['title_spoken']}")
            print(f"  - Fecha: {dup['date_spoken']}")
            print(f"  - Host: {dup['host_spoken']}")
            print(f"  - Listeners: {dup['listeners_spoken']}")
    else:
        print("No se encontraron episodios duplicados.")
    
    print(f"\n{'='*100}\n")
    
    # Guardar resultados en un archivo JSON
    output_file = 'shared/duplicates_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_duplicates': len(duplicates),
            'duplicates': duplicates
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Reporte guardado en: {output_file}\n")
    
    return duplicates

if __name__ == '__main__':
    find_duplicates()

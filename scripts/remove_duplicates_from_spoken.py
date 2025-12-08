#!/usr/bin/env python3
"""
Script para eliminar episodios duplicados de spoken_database.json
(aquellos que ya existen en episodes_database.json)
"""

import json
from pathlib import Path

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Guarda datos en un archivo JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def remove_duplicates():
    """Elimina episodios duplicados de spoken_database.json"""
    
    print("\n" + "="*100)
    print("ELIMINANDO DUPLICADOS DE SPOKEN_DATABASE.JSON")
    print("="*100 + "\n")
    
    # Cargar ambas bases de datos
    episodes_db = load_json('shared/episodes_database.json')
    spoken_db = load_json('shared/spoken_database.json')
    
    episodes_list = episodes_db.get('episodes', [])
    spoken_list = spoken_db.get('episodes', [])
    
    print(f"📊 Episodios en episodes_database.json: {len(episodes_list)}")
    print(f"📊 Episodios en spoken_database.json (antes): {len(spoken_list)}")
    
    # Crear un set de space_urls de episodes_database.json
    episodes_space_urls = set()
    for episode in episodes_list:
        space_url = episode.get('space_url', '')
        if space_url:
            episodes_space_urls.add(space_url)
    
    print(f"\n🔍 Space URLs únicos en episodes_database.json: {len(episodes_space_urls)}")
    
    # Filtrar spoken_list para eliminar duplicados
    unique_spoken = []
    duplicates_removed = []
    
    for spoken_ep in spoken_list:
        space_url = spoken_ep.get('space_url', '')
        
        # Si el episodio tiene space_url y está en episodes_database, es duplicado
        if space_url and space_url in episodes_space_urls:
            duplicates_removed.append({
                'title': spoken_ep.get('title', 'N/A'),
                'space_url': space_url,
                'date': spoken_ep.get('date', 'N/A'),
                'host': spoken_ep.get('host', 'N/A')
            })
        else:
            # No es duplicado, mantenerlo
            unique_spoken.append(spoken_ep)
    
    print(f"\n❌ Duplicados encontrados y eliminados: {len(duplicates_removed)}")
    print(f"✅ Episodios únicos restantes en spoken: {len(unique_spoken)}")
    
    # Mostrar algunos duplicados eliminados
    if duplicates_removed:
        print(f"\n{'='*100}")
        print("EJEMPLOS DE DUPLICADOS ELIMINADOS:")
        print(f"{'='*100}\n")
        
        for i, dup in enumerate(duplicates_removed[:10], 1):
            print(f"{i}. {dup['title']}")
            print(f"   Host: {dup['host']} | Fecha: {dup['date']}")
            print(f"   URL: {dup['space_url']}\n")
        
        if len(duplicates_removed) > 10:
            print(f"... y {len(duplicates_removed) - 10} duplicados más.\n")
    
    # Actualizar spoken_database.json
    spoken_db['episodes'] = unique_spoken
    
    # Actualizar metadata
    if 'metadata' in spoken_db:
        spoken_db['metadata']['total_episodes'] = len(unique_spoken)
        spoken_db['metadata']['last_updated'] = '2025-12-07'
    
    # Guardar la base de datos actualizada
    save_json(spoken_db, 'shared/spoken_database.json')
    
    print(f"{'='*100}")
    print("RESUMEN")
    print(f"{'='*100}")
    print(f"✅ spoken_database.json actualizado exitosamente")
    print(f"📊 Episodios antes: {len(spoken_list)}")
    print(f"📊 Episodios después: {len(unique_spoken)}")
    print(f"❌ Duplicados eliminados: {len(duplicates_removed)}")
    print(f"{'='*100}\n")
    
    # Guardar reporte de duplicados eliminados
    report = {
        'total_removed': len(duplicates_removed),
        'duplicates_removed': duplicates_removed
    }
    save_json(report, 'shared/duplicates_removed_report.json')
    print(f"📄 Reporte guardado en: shared/duplicates_removed_report.json\n")

if __name__ == '__main__':
    remove_duplicates()

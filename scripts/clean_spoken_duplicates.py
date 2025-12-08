#!/usr/bin/env python3
"""
Script para eliminar duplicados internos de spoken_database.json y hacer merge de la información
"""

import json
from collections import defaultdict

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Guarda datos en un archivo JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def merge_episode_data(ep1, ep2):
    """Merge dos episodios duplicados, tomando la mejor información de cada uno"""
    merged = ep1.copy()
    
    # Tomar el título más largo/completo
    if len(str(ep2.get('title', ''))) > len(str(ep1.get('title', ''))):
        merged['title'] = ep2['title']
    
    # Tomar la descripción más larga/completa
    if len(str(ep2.get('description', ''))) > len(str(ep1.get('description', ''))):
        merged['description'] = ep2['description']
    
    # Tomar el mayor número de listeners
    listeners1 = ep1.get('listeners', 0)
    listeners2 = ep2.get('listeners', 0)
    
    try:
        listeners1 = int(listeners1) if listeners1 else 0
    except:
        listeners1 = 0
    
    try:
        listeners2 = int(listeners2) if listeners2 else 0
    except:
        listeners2 = 0
    
    if listeners2 > listeners1:
        merged['listeners'] = listeners2
    
    # Tomar la duración más precisa
    dur1 = str(ep1.get('duration', ''))
    dur2 = str(ep2.get('duration', ''))
    if len(dur2) > len(dur1):
        merged['duration'] = ep2['duration']
    
    # Merge de arrays
    for field in ['guests', 'topics', 'speakers']:
        if field in ep1 or field in ep2:
            val1 = ep1.get(field, [])
            val2 = ep2.get(field, [])
            
            # Asegurar que son listas
            if not isinstance(val1, list):
                val1 = []
            if not isinstance(val2, list):
                val2 = []
            
            items1 = set(val1)
            items2 = set(val2)
            merged[field] = sorted(list(items1.union(items2)))
    
    return merged

def remove_internal_duplicates():
    """Elimina duplicados internos de spoken_database.json"""
    
    print("\n" + "="*100)
    print("ELIMINANDO DUPLICADOS INTERNOS DE SPOKEN_DATABASE.JSON")
    print("="*100 + "\n")
    
    # Cargar base de datos
    spoken_db = load_json('shared/spoken_database.json')
    spoken_list = spoken_db.get('episodes', [])
    
    print(f"📊 Episodios antes: {len(spoken_list)}")
    
    # Agrupar episodios por space_url
    episodes_by_url = defaultdict(list)
    episodes_without_url = []
    
    for ep in spoken_list:
        space_url = ep.get('space_url', '')
        if space_url:
            episodes_by_url[space_url].append(ep)
        else:
            episodes_without_url.append(ep)
    
    # Procesar duplicados
    unique_episodes = []
    duplicates_merged = []
    
    for space_url, eps in episodes_by_url.items():
        if len(eps) == 1:
            unique_episodes.append(eps[0])
        else:
            print(f"🔄 Merging {len(eps)} duplicados: {eps[0].get('title', 'N/A')[:60]}...")
            
            merged = eps[0]
            for ep in eps[1:]:
                merged = merge_episode_data(merged, ep)
            
            unique_episodes.append(merged)
            duplicates_merged.append({
                'space_url': space_url,
                'title': merged.get('title'),
                'count': len(eps)
            })
    
    # Agregar episodios sin URL
    unique_episodes.extend(episodes_without_url)
    
    # Ordenar por fecha
    unique_episodes.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    print(f"\n📊 Episodios después: {len(unique_episodes)}")
    print(f"🔄 Duplicados mergeados: {len(duplicates_merged)}")
    
    # Actualizar base de datos
    spoken_db['episodes'] = unique_episodes
    
    # Actualizar metadata
    if 'metadata' in spoken_db:
        spoken_db['metadata']['total_episodes'] = len(unique_episodes)
        spoken_db['metadata']['last_updated'] = '2025-12-07'
    
    # Guardar
    save_json(spoken_db, 'shared/spoken_database.json')
    
    print(f"\n{'='*100}")
    print("RESUMEN")
    print(f"{'='*100}")
    print(f"✅ spoken_database.json actualizado exitosamente")
    print(f"📊 Episodios antes: {len(spoken_list)}")
    print(f"📊 Episodios después: {len(unique_episodes)}")
    print(f"🔄 Duplicados eliminados y mergeados: {len(duplicates_merged)}")
    print(f"{'='*100}\n")
    
    # Guardar reporte
    report = {
        'total_merged': len(duplicates_merged),
        'duplicates_merged': duplicates_merged
    }
    save_json(report, 'shared/spoken_duplicates_merged_report.json')
    print(f"📄 Reporte guardado en: shared/spoken_duplicates_merged_report.json\n")

if __name__ == '__main__':
    remove_internal_duplicates()

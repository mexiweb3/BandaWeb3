#!/usr/bin/env python3
"""
Script para eliminar duplicados internos de episodes_database.json y hacer merge de la información
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
    
    # Convertir a int si es posible
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
    
    # Tomar la duración más precisa (la que tenga más detalle)
    dur1 = str(ep1.get('duration', ''))
    dur2 = str(ep2.get('duration', ''))
    if len(dur2) > len(dur1):
        merged['duration'] = ep2['duration']
    
    # Preferir el número sin sufijo -S7
    num1 = str(ep1.get('number', ''))
    num2 = str(ep2.get('number', ''))
    if '-S7' in num1 and '-S7' not in num2:
        merged['number'] = ep2['number']
    elif '-S7' not in num1:
        merged['number'] = ep1['number']
    
    # Merge de arrays (guests, topics, etc.)
    for field in ['guests', 'topics', 'cohosts', 'flyers']:
        if field in ep1 or field in ep2:
            items1 = set(ep1.get(field, []))
            items2 = set(ep2.get(field, []))
            merged[field] = sorted(list(items1.union(items2)))
    
    # Tomar el host más específico
    if ep2.get('host') and ep2['host'] != 'BandaWeb3' and ep1.get('host') == 'BandaWeb3':
        merged['host'] = ep2['host']
    
    return merged

def remove_internal_duplicates():
    """Elimina duplicados internos de episodes_database.json"""
    
    print("\n" + "="*100)
    print("ELIMINANDO DUPLICADOS INTERNOS DE EPISODES_DATABASE.JSON")
    print("="*100 + "\n")
    
    # Cargar base de datos
    episodes_db = load_json('shared/episodes_database.json')
    episodes_list = episodes_db.get('episodes', [])
    
    print(f"📊 Episodios antes: {len(episodes_list)}")
    
    # Agrupar episodios por space_url
    episodes_by_url = defaultdict(list)
    episodes_without_url = []
    
    for ep in episodes_list:
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
            # No hay duplicado
            unique_episodes.append(eps[0])
        else:
            # Hay duplicados, hacer merge
            print(f"🔄 Merging {len(eps)} duplicados: {eps[0].get('title', 'N/A')}")
            
            # Merge todos los duplicados
            merged = eps[0]
            for ep in eps[1:]:
                merged = merge_episode_data(merged, ep)
            
            unique_episodes.append(merged)
            duplicates_merged.append({
                'space_url': space_url,
                'title': merged.get('title'),
                'count': len(eps),
                'numbers': [ep.get('number') for ep in eps]
            })
    
    # Agregar episodios sin URL
    unique_episodes.extend(episodes_without_url)
    
    # Ordenar por fecha (más reciente primero)
    unique_episodes.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    print(f"\n📊 Episodios después: {len(unique_episodes)}")
    print(f"🔄 Duplicados mergeados: {len(duplicates_merged)}")
    
    # Mostrar duplicados mergeados
    if duplicates_merged:
        print(f"\n{'='*100}")
        print("DUPLICADOS MERGEADOS:")
        print(f"{'='*100}\n")
        
        for i, dup in enumerate(duplicates_merged, 1):
            print(f"{i}. {dup['title']}")
            print(f"   Números originales: {', '.join(map(str, dup['numbers']))}")
            print(f"   Space URL: {dup['space_url']}\n")
    
    # Actualizar base de datos
    episodes_db['episodes'] = unique_episodes
    
    # Actualizar metadata
    if 'metadata' in episodes_db:
        episodes_db['metadata']['total_episodes'] = len(unique_episodes)
        episodes_db['metadata']['last_updated'] = '2025-12-07'
    
    # Guardar
    save_json(episodes_db, 'shared/episodes_database.json')
    
    print(f"{'='*100}")
    print("RESUMEN")
    print(f"{'='*100}")
    print(f"✅ episodes_database.json actualizado exitosamente")
    print(f"📊 Episodios antes: {len(episodes_list)}")
    print(f"📊 Episodios después: {len(unique_episodes)}")
    print(f"🔄 Duplicados eliminados y mergeados: {len(duplicates_merged)}")
    print(f"{'='*100}\n")
    
    # Guardar reporte
    report = {
        'total_merged': len(duplicates_merged),
        'duplicates_merged': duplicates_merged
    }
    save_json(report, 'shared/episodes_duplicates_merged_report.json')
    print(f"📄 Reporte guardado en: shared/episodes_duplicates_merged_report.json\n")

if __name__ == '__main__':
    remove_internal_duplicates()

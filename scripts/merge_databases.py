#!/usr/bin/env python3
"""
Script para consolidar episodes_database.json y spoken_database.json en una sola base de datos
sin duplicados, ordenada por fecha (más reciente primero)
"""

import json
from datetime import datetime
from pathlib import Path

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Guarda datos en un archivo JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_date(date_str):
    """Convierte una fecha string a objeto datetime para ordenar"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        # Si falla, retornar una fecha muy antigua
        return datetime(1900, 1, 1)

def merge_databases():
    """Fusiona las dos bases de datos eliminando duplicados"""
    
    print("\n" + "="*100)
    print("CONSOLIDANDO BASES DE DATOS")
    print("="*100 + "\n")
    
    # Cargar ambas bases de datos
    episodes_db = load_json('shared/episodes_database.json')
    spoken_db = load_json('shared/spoken_database.json')
    
    episodes_list = episodes_db.get('episodes', [])
    spoken_list = spoken_db.get('episodes', [])
    
    print(f"📊 Episodios en episodes_database.json: {len(episodes_list)}")
    print(f"📊 Episodios en spoken_database.json: {len(spoken_list)}")
    
    # Crear un diccionario para rastrear episodios únicos por space_url
    unique_episodes = {}
    
    # Primero agregar todos los episodios de episodes_database.json
    for episode in episodes_list:
        space_url = episode.get('space_url', '')
        if space_url:
            unique_episodes[space_url] = episode
        else:
            # Si no tiene space_url, usar una clave única basada en otros campos
            key = f"{episode.get('date', '')}_{episode.get('title', '')}_{episode.get('number', '')}"
            if key not in unique_episodes:
                unique_episodes[key] = episode
    
    print(f"\n✅ Episodios únicos de episodes_database.json: {len(unique_episodes)}")
    
    # Agregar episodios de spoken_database.json que no estén duplicados
    added_from_spoken = 0
    for episode in spoken_list:
        space_url = episode.get('space_url', '')
        
        if space_url:
            if space_url not in unique_episodes:
                unique_episodes[space_url] = episode
                added_from_spoken += 1
        else:
            # Si no tiene space_url, usar una clave única
            key = f"{episode.get('date', '')}_{episode.get('title', '')}_{episode.get('number', '')}"
            if key not in unique_episodes:
                unique_episodes[key] = episode
                added_from_spoken += 1
    
    print(f"✅ Episodios únicos agregados de spoken_database.json: {added_from_spoken}")
    
    # Convertir el diccionario a lista
    merged_episodes = list(unique_episodes.values())
    
    # Ordenar por fecha (más reciente primero)
    merged_episodes.sort(key=lambda x: parse_date(x.get('date', '1900-01-01')), reverse=True)
    
    print(f"\n🎯 Total de episodios únicos en la base de datos consolidada: {len(merged_episodes)}")
    
    # Calcular estadísticas
    total_episodes = len(merged_episodes)
    episodes_with_listeners = sum(1 for ep in merged_episodes if ep.get('listeners'))
    total_listeners = sum(ep.get('listeners', 0) for ep in merged_episodes if isinstance(ep.get('listeners'), (int, float)))
    avg_listeners = total_listeners / episodes_with_listeners if episodes_with_listeners > 0 else 0
    
    # Contar por tipo
    type_breakdown = {}
    for ep in merged_episodes:
        ep_type = ep.get('type', 'unknown')
        type_breakdown[ep_type] = type_breakdown.get(ep_type, 0) + 1
    
    # Calcular duración total
    total_duration_seconds = 0
    episodes_with_duration = 0
    for ep in merged_episodes:
        duration = ep.get('duration', '')
        if duration and isinstance(duration, str):
            try:
                parts = duration.split(':')
                if len(parts) == 3:  # HH:MM:SS
                    hours, minutes, seconds = map(int, parts)
                    total_duration_seconds += hours * 3600 + minutes * 60 + seconds
                    episodes_with_duration += 1
                elif len(parts) == 2:  # MM:SS
                    minutes, seconds = map(int, parts)
                    total_duration_seconds += minutes * 60 + seconds
                    episodes_with_duration += 1
            except:
                pass
    
    avg_duration_seconds = total_duration_seconds / episodes_with_duration if episodes_with_duration > 0 else 0
    avg_duration_formatted = f"{int(avg_duration_seconds // 3600):02d}:{int((avg_duration_seconds % 3600) // 60):02d}:{int(avg_duration_seconds % 60):02d}"
    total_duration_formatted = f"{int(total_duration_seconds // 3600):02d}:{int((total_duration_seconds % 3600) // 60):02d}:{int(total_duration_seconds % 60):02d}"
    
    # Crear la nueva base de datos consolidada
    consolidated_db = {
        "metadata": {
            "podcast_name": "BandaWeb3 - Consolidated Database",
            "description": "Base de datos consolidada de todos los episodios de BandaWeb3 (hosted, co-hosted y spoken)",
            "host": "BandaWeb3",
            "language": "es",
            "categories": [
                "Technology",
                "Web3",
                "Blockchain",
                "Cryptocurrency"
            ],
            "website": "https://bandaweb3.com",
            "twitter": "@BandaWeb3",
            "last_updated": datetime.now().strftime('%Y-%m-%d'),
            "total_episodes": total_episodes,
            "statistics": {
                "total_episodes": total_episodes,
                "total_duration": total_duration_formatted,
                "average_duration": avg_duration_formatted,
                "total_listeners": total_listeners,
                "average_listeners": round(avg_listeners, 2),
                "episodes_with_listener_data": episodes_with_listeners,
                "breakdown_by_type": type_breakdown
            }
        },
        "episodes": merged_episodes
    }
    
    # Guardar la base de datos consolidada
    output_file = 'shared/consolidated_database.json'
    save_json(consolidated_db, output_file)
    
    print(f"\n{'='*100}")
    print("ESTADÍSTICAS DE LA BASE DE DATOS CONSOLIDADA")
    print(f"{'='*100}")
    print(f"\n📊 Total de episodios: {total_episodes}")
    print(f"⏱️  Duración total: {total_duration_formatted}")
    print(f"⏱️  Duración promedio: {avg_duration_formatted}")
    print(f"👥 Total de oyentes: {total_listeners:,}")
    print(f"👥 Promedio de oyentes: {avg_listeners:.2f}")
    print(f"📈 Episodios con datos de oyentes: {episodes_with_listeners}")
    print(f"\n📂 Desglose por tipo:")
    for ep_type, count in sorted(type_breakdown.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {ep_type}: {count}")
    
    print(f"\n✅ Base de datos consolidada guardada en: {output_file}")
    print(f"{'='*100}\n")
    
    return consolidated_db

if __name__ == '__main__':
    merge_databases()

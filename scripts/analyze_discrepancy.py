#!/usr/bin/env python3
"""
Script para analizar la discrepancia de 29 episodios
"""

import json
from collections import Counter

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_discrepancy():
    """Analiza la discrepancia entre las bases de datos"""
    
    print("\n" + "="*100)
    print("ANÁLISIS DE DISCREPANCIA")
    print("="*100 + "\n")
    
    # Cargar bases de datos
    episodes_db = load_json('shared/episodes_database.json')
    spoken_db = load_json('shared/spoken_database.json')
    
    episodes_list = episodes_db.get('episodes', [])
    spoken_list = spoken_db.get('episodes', [])
    
    print(f"📊 Episodios en episodes_database.json: {len(episodes_list)}")
    print(f"📊 Episodios en spoken_database.json: {len(spoken_list)}")
    print(f"📊 Suma: {len(episodes_list) + len(spoken_list)}")
    
    # Verificar duplicados internos en episodes_database
    episodes_urls = [ep.get('space_url', '') for ep in episodes_list if ep.get('space_url')]
    episodes_url_counts = Counter(episodes_urls)
    episodes_internal_dups = {url: count for url, count in episodes_url_counts.items() if count > 1}
    
    print(f"\n🔍 Duplicados internos en episodes_database.json: {len(episodes_internal_dups)}")
    if episodes_internal_dups:
        for url, count in episodes_internal_dups.items():
            print(f"   - {url}: {count} veces")
    
    # Verificar duplicados internos en spoken_database
    spoken_urls = [ep.get('space_url', '') for ep in spoken_list if ep.get('space_url')]
    spoken_url_counts = Counter(spoken_urls)
    spoken_internal_dups = {url: count for url, count in spoken_url_counts.items() if count > 1}
    
    print(f"\n🔍 Duplicados internos en spoken_database.json: {len(spoken_internal_dups)}")
    if spoken_internal_dups:
        total_internal_dups = sum(count - 1 for count in spoken_internal_dups.values())
        print(f"   Total de registros duplicados: {total_internal_dups}")
        for url, count in list(spoken_internal_dups.items())[:10]:
            print(f"   - {url}: {count} veces")
        if len(spoken_internal_dups) > 10:
            print(f"   ... y {len(spoken_internal_dups) - 10} más")
    
    # Contar episodios sin space_url
    episodes_no_url = sum(1 for ep in episodes_list if not ep.get('space_url'))
    spoken_no_url = sum(1 for ep in spoken_list if not ep.get('space_url'))
    
    print(f"\n📝 Episodios sin space_url:")
    print(f"   - episodes_database.json: {episodes_no_url}")
    print(f"   - spoken_database.json: {spoken_no_url}")
    
    # Calcular total de duplicados internos
    total_episodes_internal = sum(count - 1 for count in episodes_url_counts.values() if count > 1)
    total_spoken_internal = sum(count - 1 for count in spoken_url_counts.values() if count > 1)
    total_internal = total_episodes_internal + total_spoken_internal
    
    print(f"\n📊 RESUMEN:")
    print(f"   - Total duplicados internos en episodes: {total_episodes_internal}")
    print(f"   - Total duplicados internos en spoken: {total_spoken_internal}")
    print(f"   - Total duplicados internos: {total_internal}")
    print(f"   - Discrepancia esperada vs real: 29 vs {total_internal}")
    
    print(f"\n{'='*100}\n")
    
    # Mostrar algunos ejemplos de duplicados internos en spoken
    if spoken_internal_dups:
        print("EJEMPLOS DE DUPLICADOS INTERNOS EN SPOKEN_DATABASE.JSON:")
        print("="*100 + "\n")
        
        for i, (url, count) in enumerate(list(spoken_internal_dups.items())[:5], 1):
            # Encontrar los episodios con este URL
            matching_eps = [ep for ep in spoken_list if ep.get('space_url') == url]
            print(f"{i}. Space URL: {url}")
            print(f"   Aparece {count} veces:")
            for j, ep in enumerate(matching_eps, 1):
                print(f"   {j}) {ep.get('title', 'N/A')} - {ep.get('date', 'N/A')} - {ep.get('host', 'N/A')}")
            print()

if __name__ == '__main__':
    analyze_discrepancy()

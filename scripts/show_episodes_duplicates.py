#!/usr/bin/env python3
"""
Script para mostrar detalles de los duplicados en episodes_database.json
"""

import json

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def show_duplicate_details():
    """Muestra detalles de los duplicados en episodes_database.json"""
    
    # URLs duplicadas
    duplicate_urls = [
        'https://x.com/i/spaces/1vOxwjWdZvDJB',
        'https://x.com/i/spaces/1gqGvQzEDQeKB',
        'https://x.com/i/spaces/1gqxvQkyovRJB',
        'https://x.com/i/spaces/1RDGlazORNNJL',
        'https://x.com/i/spaces/1BRJjZPNmzLJw',
        'https://x.com/i/spaces/1LyxBqbQPYLJN',
        'https://x.com/i/spaces/1zqKVPozepnJB'
    ]
    
    # Cargar base de datos
    episodes_db = load_json('shared/episodes_database.json')
    episodes_list = episodes_db.get('episodes', [])
    
    print("\n" + "="*100)
    print("DETALLES DE DUPLICADOS EN EPISODES_DATABASE.JSON")
    print("="*100 + "\n")
    
    for i, url in enumerate(duplicate_urls, 1):
        # Encontrar todos los episodios con este URL
        matching_eps = [ep for ep in episodes_list if ep.get('space_url') == url]
        
        if matching_eps:
            print(f"{i}. DUPLICADO #{i}")
            print(f"   Space URL: {url}")
            print(f"   Aparece {len(matching_eps)} veces\n")
            
            for j, ep in enumerate(matching_eps, 1):
                print(f"   OCURRENCIA {j}:")
                print(f"   ├─ Número: {ep.get('number', 'N/A')}")
                print(f"   ├─ Título: {ep.get('title', 'N/A')}")
                print(f"   ├─ Fecha: {ep.get('date', 'N/A')}")
                print(f"   ├─ Host: {ep.get('host', 'N/A')}")
                print(f"   ├─ Duración: {ep.get('duration', 'N/A')}")
                print(f"   ├─ Listeners: {ep.get('listeners', 'N/A')}")
                print(f"   ├─ Tipo: {ep.get('type', 'N/A')}")
                
                desc = ep.get('description', 'N/A')
                if len(desc) > 150:
                    desc = desc[:150] + "..."
                print(f"   └─ Descripción: {desc}")
                print()
            
            print("-" * 100 + "\n")
        else:
            print(f"{i}. URL no encontrado: {url}\n")
    
    print("="*100 + "\n")

if __name__ == '__main__':
    show_duplicate_details()

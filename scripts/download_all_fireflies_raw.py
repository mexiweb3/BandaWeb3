#!/usr/bin/env python3
"""
Script para descargar TODOS los transcripts de Fireflies.ai como JSON raw
Sin procesamiento, solo descarga los 544 transcripts
"""
import os
import requests
import json
from pathlib import Path
import time

# Configuración
ENV_FILE = Path(".env")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"
OUTPUT_DIR = Path("shared/fireflies_all_raw")

def load_fireflies_api_key():
    """Carga la API key de Fireflies desde el archivo .env"""
    if not ENV_FILE.exists():
        return None
    
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key == 'FIREFLIES_API_KEY':
                        return value.strip()
    return None

def get_all_transcripts(api_key):
    """Obtiene la lista de todos los transcripts disponibles usando paginación"""
    
    query = """
    query Transcripts($limit: Int, $skip: Int) {
        transcripts(limit: $limit, skip: $skip) {
            id
            title
            date
            duration
        }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    all_transcripts = []
    limit = 50
    skip = 0
    
    while True:
        payload = {
            "query": query,
            "variables": {
                "limit": limit,
                "skip": skip
            }
        }
        
        try:
            print(f"   ⏳ Solicitando batch (skip={skip})...")
            response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'errors' in result:
                    print(f"❌ Error en GraphQL: {result['errors']}")
                    break
                
                batch = result.get('data', {}).get('transcripts', [])
                if not batch:
                    break
                    
                all_transcripts.extend(batch)
                print(f"   ✅ Recibidos {len(batch)} transcripts")
                
                if len(batch) < limit:
                    break
                    
                skip += limit
                time.sleep(0.5)
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                break
        except Exception as e:
            print(f"❌ Error: {e}")
            break
            
    return all_transcripts

def get_transcript_details(transcript_id, api_key):
    """Obtiene los detalles completos de un transcript"""
    
    query = """
    query Transcript($id: String!) {
        transcript(id: $id) {
            id
            title
            date
            duration
            speakers {
                id
                name
            }
            sentences {
                index
                speaker_name
                speaker_id
                text
                raw_text
                start_time
                end_time
            }
        }
    }
    """
    
    variables = {
        "id": transcript_id
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "query": query,
        "variables": variables
    }
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                return None
            return result.get('data', {}).get('transcript', {})
        else:
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print("=" * 80)
    print("FIREFLIES.AI - DESCARGA COMPLETA (TODOS LOS TRANSCRIPTS)")
    print("=" * 80)
    print()
    
    # Crear directorio de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cargar API key
    api_key = load_fireflies_api_key()
    if not api_key:
        print("❌ Por favor configura tu FIREFLIES_API_KEY en el archivo .env")
        return
    
    # Obtener lista de transcripts
    print("🔍 Consultando transcripts disponibles en Fireflies...")
    all_transcripts = get_all_transcripts(api_key)
    
    if not all_transcripts:
        print("❌ No se encontraron transcripts o hubo un error")
        return
    
    print(f"✅ Encontrados {len(all_transcripts)} transcripts en Fireflies")
    print()
    
    # Descargar cada transcript
    downloaded = 0
    failed = 0
    
    for i, transcript in enumerate(all_transcripts, 1):
        transcript_id = transcript.get('id')
        title = transcript.get('title', 'Unknown')
        
        # Usar el ID de Fireflies como nombre de archivo
        output_file = OUTPUT_DIR / f"{transcript_id}.json"
        
        # Verificar si ya existe
        if output_file.exists():
            print(f"[{i}/{len(all_transcripts)}] ⏭️  Ya existe: {title[:60]}...")
            continue
        
        print(f"[{i}/{len(all_transcripts)}] 📥 Descargando: {title[:60]}...")
        
        # Obtener detalles completos
        details = get_transcript_details(transcript_id, api_key)
        
        if details:
            # Guardar JSON completo
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(details, f, indent=2, ensure_ascii=False)
            
            print(f"            ✅ Guardado: {transcript_id}.json")
            downloaded += 1
        else:
            print(f"            ❌ Error al descargar")
            failed += 1
        
        # Pausa para no saturar la API
        time.sleep(0.3)
    
    print()
    print("=" * 80)
    print("📊 RESUMEN DE DESCARGA")
    print("=" * 80)
    print(f"✅ Descargados: {downloaded}")
    print(f"❌ Fallidos: {failed}")
    print(f"📁 Total transcripts: {len(all_transcripts)}")
    print()
    print(f"📂 Archivos guardados en: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

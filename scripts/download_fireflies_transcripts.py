#!/usr/bin/env python3
"""
Script para descargar transcripciones completadas de Fireflies.ai
"""
import os
import requests
import json
from pathlib import Path
import time

# Configuración
ENV_FILE = Path(".env")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"
OUTPUT_DIR = Path("shared/transcriptions_fireflies")
UPLOAD_RECORDS_DIR = OUTPUT_DIR

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
                time.sleep(0.5)  # Breve pausa para no saturar
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
                print(f"DEBUG GRAPHQL ERROR: {result['errors']}")
                return None
            return result.get('data', {}).get('transcript', {})
        else:
            return None
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return None

def find_space_id_by_title(title):
    """Busca el space_id en los upload records por título"""
    try:
        upload_records = list(UPLOAD_RECORDS_DIR.glob("*_upload_record.json"))
        
        for record_file in upload_records:
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    record = json.load(f)
                    if record.get('title') == title:
                        return record.get('space_id')
            except:
                continue
    except Exception as e:
        print(f"⚠️ Error buscando space_id: {e}")
        return None
    
    return None

def load_database():
    """Carga la base de datos de episodios para obtener metadatos"""
    try:
        with open("shared/episodes_database.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  No se pudo cargar episodes_database.json: {e}")
        return {}

def find_episode_in_db(space_id, db_data):
    """Busca un episodio en la BD usando el space_id"""
    if not space_id:
        return None
    if not db_data or "episodes" not in db_data:
        return None
        
    for ep in db_data["episodes"]:
        url = ep.get("space_url") or ""
        if space_id in url:
            return ep
    return None

def generate_formatted_transcript(transcript_data, episode_metadata=None):
    """Genera un archivo TXT formateado con la transcripción y metadatos"""
    lines = []
    
    # 1. Header estilo Deepgram (con metadatos enriquecidos si existen)
    lines.append("=" * 80)
    lines.append("INFORMACIÓN DEL EPISODIO")
    lines.append("=" * 80)
    
    if episode_metadata:
        ep_id = episode_metadata.get('id', 'N/A')
        title = episode_metadata.get('title', transcript_data.get('title', 'N/A'))
        date = episode_metadata.get('date', 'N/A')
        host = episode_metadata.get('host', 'N/A')
        type_ = episode_metadata.get('type', 'hosted')
        desc = episode_metadata.get('description', '')
        duration = episode_metadata.get('duration', 'N/A')
        listeners = episode_metadata.get('live_listeners', 'N/A')
        
        lines.append(f"Episodio: #{ep_id}")
        lines.append(f"Título: {title}")
        lines.append(f"Fecha: {date}")
        lines.append(f"Host: {host}")
        lines.append(f"Tipo: {type_}")
        lines.append("")
        lines.append("Descripción:")
        lines.append(desc)
        lines.append("")
        lines.append(f"Duración: {duration}")
        lines.append(f"Escuchas: {listeners}")
        lines.append("")
        lines.append("Links:")
        if episode_metadata.get('space_url'):
            lines.append(f"  Space: {episode_metadata.get('space_url')}")
    else:
        # Fallback si no hay metadatos de BD
        lines.append(f"Título: {transcript_data.get('title', 'N/A')}")
        lines.append(f"Fecha: {transcript_data.get('date', 'N/A')}")
        lines.append(f"Duración: {transcript_data.get('duration', 'N/A')} segundos")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("TRANSCRIPCIÓN")
    lines.append("=" * 80)
    lines.append("")
    
    # Transcripción con speakers
    if transcript_data.get('sentences'):
        current_speaker = None
        for sentence in transcript_data['sentences']:
            speaker = sentence.get('speaker_name') or f"Speaker {sentence.get('speaker_id', 'N/A')}"
            text = sentence.get('text', '')
            start = sentence.get('start_time', 0)
            
            # Format time as HH:MM:SS
            m, s = divmod(start, 60)
            h, m = divmod(m, 60)
            timestamp = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
            
            # Agrupar por speaker
            if speaker != current_speaker:
                if current_speaker is not None:
                    lines.append("")
                lines.append(f"[{speaker} - {timestamp}]")
                current_speaker = speaker
            
            lines.append(text)
    
    return "\n".join(lines)

def main():
    print("=" * 80)
    print("FIREFLIES.AI - DESCARGA DE TRANSCRIPCIONES")
    print("=" * 80)
    print()
    
    # Verificar API key
    api_key = load_fireflies_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Por favor configura tu FIREFLIES_API_KEY en el archivo .env")
        return
    
    # Cargar base de datos de episodios
    db_data = load_database()
    
    # Obtener lista de transcripts
    print("🔍 Consultando transcripts disponibles en Fireflies...")
    all_transcripts = get_all_transcripts(api_key)
    
    if not all_transcripts:
        print("❌ No se encontraron transcripts o hubo un error")
        return
    
    print(f"✅ Encontrados {len(all_transcripts)} transcripts en Fireflies")
    print()
    
    # Filtrar solo los de BandaWeb3
    bandaweb3_transcripts = [t for t in all_transcripts if 'BandaWeb3' in t.get('title', '')]
    print(f"📊 {len(bandaweb3_transcripts)} transcripts de BandaWeb3")
    print()
    
    # Descargar cada transcript
    downloaded = 0
    updated = 0
    failed = 0
    
    for i, transcript in enumerate(bandaweb3_transcripts, 1):
        transcript_id = transcript.get('id')
        title = transcript.get('title', 'Unknown')
        
        # Buscar space_id
        space_id = find_space_id_by_title(title)
        
        # Si no lo encontramos por título exacto en records, intentar buscar en DB
        
        # Fallback Logic existing
        if not space_id:
             # Try extracting from title if it looks like an ID? No, usually not in title.
             # Just use fallback ID for file, but try to find metadata anyway.
             print(f"[{i}/{len(bandaweb3_transcripts)}] ⚠️  No se encontró space_id para: {title[:50]}...")
             space_id = transcript_id[:15]
        
        # Buscar metadatos del episodio
        episode_metadata = find_episode_in_db(space_id, db_data)
        
        output_file = OUTPUT_DIR / f"{space_id}_fireflies.json"
        txt_file = OUTPUT_DIR / f"{space_id}_fireflies.txt"
        
        # SIEMPRE redescargar para asegurar speaker_id y datos frescos
        print(f"[{i}/{len(bandaweb3_transcripts)}] 🔄 Procesando: {title[:50]}...")
        
        # Obtener detalles completos
        details = get_transcript_details(transcript_id, api_key)
        
        if details and details.get('sentences'):
            # Guardar JSON completo
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(details, f, indent=2, ensure_ascii=False)
            
            # Guardar TXT formateado usando metadatos
            formatted_text = generate_formatted_transcript(details, episode_metadata)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            
            meta_status = "✅ Metadatos" if episode_metadata else "⚠️ Sin Metadatos"
            print(f"            ✅ Guardado y actualizado ({meta_status})")
            updated += 1
        else:
            print(f"            ❌ Error al descargar detalles")
            failed += 1
        
        # Pausa para no saturar la API
        time.sleep(0.5)
    
    print()
    print("=" * 80)
    print("📊 RESUMEN DE ACTUALIZACIÓN")
    print("=" * 80)
    print(f"🔄 Total procesados/actualizados: {updated}")
    print(f"❌ Fallidos: {failed}")
    print(f"📁 Transcripts de BandaWeb3: {len(bandaweb3_transcripts)}")
    print()
    print(f"📂 Archivos guardados en: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

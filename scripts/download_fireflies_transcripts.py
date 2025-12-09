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
    """Obtiene la lista de todos los transcripts disponibles"""
    
    query = """
    query Transcripts {
        transcripts {
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
    
    payload = {
        "query": query
    }
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"❌ Error en GraphQL: {result['errors']}")
                return []
            return result.get('data', {}).get('transcripts', [])
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def get_transcript_details(transcript_id, api_key):
    """Obtiene los detalles completos de un transcript"""
    
    query = """
    query Transcript($transcriptId: String!) {
        transcript(id: $transcriptId) {
            id
            title
            date
            duration
            sentences {
                text
                speaker_name
                speaker_id
                start_time
                end_time
            }
            summary {
                overview
                keywords
                action_items
                outline
                shorthand_bullet
            }
            topics {
                text
                start_time
                end_time
            }
            participants {
                name
                email
            }
            speaker_time {
                speaker_name
                total_time
                percentage
            }
        }
    }
    """
    
    variables = {
        "transcriptId": transcript_id
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
    upload_records = list(UPLOAD_RECORDS_DIR.glob("*_upload_record.json"))
    
    for record_file in upload_records:
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                record = json.load(f)
                if record.get('title') == title:
                    return record.get('space_id')
        except:
            continue
    
    return None

def generate_formatted_transcript(transcript_data):
    """Genera un archivo TXT formateado con la transcripción"""
    lines = []
    
    # Header con información del episodio
    lines.append("=" * 80)
    lines.append("TRANSCRIPCIÓN FIREFLIES.AI")
    lines.append("=" * 80)
    lines.append(f"Título: {transcript_data.get('title', 'N/A')}")
    lines.append(f"Fecha: {transcript_data.get('date', 'N/A')}")
    lines.append(f"Duración: {transcript_data.get('duration', 'N/A')} segundos")
    lines.append("")
    
    # Resumen
    if transcript_data.get('summary'):
        summary = transcript_data['summary']
        lines.append("=" * 80)
        lines.append("RESUMEN")
        lines.append("=" * 80)
        
        if summary.get('overview'):
            lines.append(summary['overview'])
            lines.append("")
        
        if summary.get('keywords'):
            lines.append("🏷️  KEYWORDS:")
            lines.append(", ".join(summary['keywords']))
            lines.append("")
        
        if summary.get('action_items'):
            lines.append("✅ ACTION ITEMS:")
            for item in summary['action_items']:
                lines.append(f"  - {item}")
            lines.append("")
        
        if summary.get('shorthand_bullet'):
            lines.append("📝 PUNTOS CLAVE:")
            lines.append(summary['shorthand_bullet'])
            lines.append("")
    
    # Temas
    if transcript_data.get('topics'):
        lines.append("=" * 80)
        lines.append("TEMAS DISCUTIDOS")
        lines.append("=" * 80)
        for topic in transcript_data['topics']:
            start = topic.get('start_time', 0)
            lines.append(f"[{start:.1f}s] {topic.get('text', '')}")
        lines.append("")
    
    # Métricas de participación
    if transcript_data.get('speaker_time'):
        lines.append("=" * 80)
        lines.append("MÉTRICAS DE PARTICIPACIÓN")
        lines.append("=" * 80)
        for speaker in transcript_data['speaker_time']:
            name = speaker.get('speaker_name', 'Unknown')
            time_val = speaker.get('total_time', 0)
            percentage = speaker.get('percentage', 0)
            lines.append(f"{name}: {time_val:.1f}s ({percentage:.1f}%)")
        lines.append("")
    
    # Transcripción completa
    lines.append("=" * 80)
    lines.append("TRANSCRIPCIÓN COMPLETA")
    lines.append("=" * 80)
    lines.append("")
    
    if transcript_data.get('sentences'):
        current_speaker = None
        for sentence in transcript_data['sentences']:
            speaker = sentence.get('speaker_name', f"Speaker {sentence.get('speaker_id', 'N/A')}")
            text = sentence.get('text', '')
            start = sentence.get('start_time', 0)
            
            # Agrupar por speaker
            if speaker != current_speaker:
                if current_speaker is not None:
                    lines.append("")
                lines.append(f"[{speaker} - {start:.1f}s]")
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
    skipped = 0
    failed = 0
    
    for i, transcript in enumerate(bandaweb3_transcripts, 1):
        transcript_id = transcript.get('id')
        title = transcript.get('title', 'Unknown')
        
        # Buscar space_id
        space_id = find_space_id_by_title(title)
        if not space_id:
            print(f"[{i}/{len(bandaweb3_transcripts)}] ⚠️  No se encontró space_id para: {title[:50]}...")
            space_id = transcript_id[:15]  # Usar parte del ID como fallback
        
        # Verificar si ya existe
        output_file = OUTPUT_DIR / f"{space_id}_fireflies.json"
        txt_file = OUTPUT_DIR / f"{space_id}_fireflies.txt"
        
        if output_file.exists() and txt_file.exists():
            print(f"[{i}/{len(bandaweb3_transcripts)}] ⏭️  Ya existe: {title[:50]}...")
            skipped += 1
            continue
        
        print(f"[{i}/{len(bandaweb3_transcripts)}] 📥 Descargando: {title[:50]}...")
        
        # Obtener detalles completos
        details = get_transcript_details(transcript_id, api_key)
        
        if details and details.get('sentences'):
            # Guardar JSON completo
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(details, f, indent=2, ensure_ascii=False)
            
            # Guardar TXT formateado
            formatted_text = generate_formatted_transcript(details)
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            
            print(f"            ✅ Guardado: {space_id}")
            downloaded += 1
        else:
            print(f"            ❌ Error al descargar")
            failed += 1
        
        # Pausa para no saturar la API
        time.sleep(1)
    
    print()
    print("=" * 80)
    print("📊 RESUMEN DE DESCARGA")
    print("=" * 80)
    print(f"✅ Descargados: {downloaded}")
    print(f"⏭️  Ya existían: {skipped}")
    print(f"❌ Fallidos: {failed}")
    print(f"📁 Total procesados: {len(bandaweb3_transcripts)}")
    print()
    print(f"📂 Archivos guardados en: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

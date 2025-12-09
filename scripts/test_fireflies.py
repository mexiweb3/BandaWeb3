#!/usr/bin/env python3
"""
Script para probar Fireflies.ai usando transfer.sh como almacenamiento temporal
"""
import os
import requests
import json
from pathlib import Path
import time
import subprocess

# Configuración
ENV_FILE = Path(".env")
AUDIO_DIR = Path("shared/audio")
TEST_FILE = "1kvJpbwePbwKE.mp3"  # Episodio de prueba
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"

def load_fireflies_api_key():
    """Carga la API key de Fireflies desde el archivo .env"""
    if not ENV_FILE.exists():
        print("❌ Error: No se encontró el archivo .env")
        return None
    
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key == 'FIREFLIES_API_KEY':
                        return value.strip()
    return None

def upload_to_fileio(file_path):
    """
    Sube un archivo a file.io y devuelve la URL pública
    
    Args:
        file_path: Path al archivo local
    
    Returns:
        str: URL HTTPS del archivo
    """
    print(f"📤 Subiendo {file_path.name} a file.io...")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('https://file.io', files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                url = result.get('link')
                print(f"✅ Archivo subido: {url}")
                print(f"⚠️  Nota: Este link expira después de 1 descarga o 14 días")
                return url
            else:
                print(f"❌ Error: {result.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def upload_audio_to_fireflies(audio_url, title, api_key, language='es'):
    """Sube un archivo de audio a Fireflies para transcripción"""
    
    mutation = """
    mutation UploadAudio($input: AudioUploadInput!) {
        uploadAudio(input: $input) {
            success
            title
            transcript_id
            message
        }
    }
    """
    
    variables = {
        "input": {
            "url": audio_url,
            "title": title,
            "custom_language": language
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "query": mutation,
        "variables": variables
    }
    
    print(f"\n🔥 Enviando a Fireflies API...")
    print(f"   Título: {title}")
    print(f"   Idioma: {language}")
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"❌ Error en GraphQL:")
                print(json.dumps(result['errors'], indent=2))
                return None
            return result.get('data', {}).get('uploadAudio', {})
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def get_transcript(transcript_id, api_key):
    """Obtiene la transcripción de Fireflies"""
    
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
            }
            participants {
                name
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
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"❌ Error en GraphQL:")
                print(json.dumps(result['errors'], indent=2))
                return None
            return result.get('data', {}).get('transcript', {})
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 80)
    print("FIREFLIES.AI - PRUEBA DE TRANSCRIPCIÓN")
    print("=" * 80)
    print()
    
    # Verificar API key
    api_key = load_fireflies_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Por favor configura tu FIREFLIES_API_KEY en el archivo .env")
        print("\nPara obtener tu API key:")
        print("1. Ve a https://app.fireflies.ai/")
        print("2. Settings > Integrations > API")
        print("3. Copia tu API key y agrégala al archivo .env")
        return
    
    # Verificar archivo de prueba
    test_path = AUDIO_DIR / TEST_FILE
    if not test_path.exists():
        print(f"❌ No se encontró el archivo de prueba: {TEST_FILE}")
        return
    
    print(f"📁 Archivo de prueba: {TEST_FILE}")
    print(f"   Tamaño: {test_path.stat().st_size / (1024*1024):.2f} MB")
    print()
    
    # Paso 1: Subir archivo a file.io
    audio_url = upload_to_fileio(test_path)
    if not audio_url:
        print("❌ No se pudo subir el archivo")
        return
    
    # Paso 2: Enviar a Fireflies
    result = upload_audio_to_fireflies(
        audio_url=audio_url,
        title="BandaWeb3 #002 - Prueba Fireflies",
        api_key=api_key,
        language='es'
    )
    
    if not result:
        print("❌ No se pudo enviar a Fireflies")
        return
    
    if not result.get('success'):
        print(f"❌ Fireflies rechazó el archivo: {result.get('message', 'Sin mensaje')}")
        return
    
    transcript_id = result.get('transcript_id')
    print(f"\n✅ Audio enviado exitosamente!")
    print(f"   Transcript ID: {transcript_id}")
    print(f"   Mensaje: {result.get('message', 'N/A')}")
    print()
    print("⏳ Esperando procesamiento (esto puede tomar varios minutos)...")
    print("   Fireflies procesará el audio y generará la transcripción")
    print()
    
    # Paso 3: Esperar y obtener transcripción
    max_attempts = 20
    wait_time = 30  # segundos entre intentos
    
    for attempt in range(1, max_attempts + 1):
        print(f"🔍 Intento {attempt}/{max_attempts} - Consultando transcripción...")
        
        transcript = get_transcript(transcript_id, api_key)
        
        if transcript and transcript.get('sentences'):
            print(f"\n✅ ¡Transcripción completada!")
            print(f"   Duración: {transcript.get('duration', 'N/A')} segundos")
            print(f"   Participantes: {len(transcript.get('participants', []))}")
            print(f"   Oraciones: {len(transcript.get('sentences', []))}")
            
            # Guardar resultado
            output_path = Path("shared/transcriptions") / f"{TEST_FILE.replace('.mp3', '')}_fireflies.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Transcripción guardada: {output_path}")
            
            # Mostrar muestra
            print(f"\n📝 Muestra de la transcripción:")
            print("=" * 80)
            for i, sentence in enumerate(transcript.get('sentences', [])[:5]):
                speaker = sentence.get('speaker_name', f"Speaker {sentence.get('speaker_id', 'N/A')}")
                text = sentence.get('text', '')
                start = sentence.get('start_time', 0)
                print(f"[{speaker} - {start:.1f}s] {text}")
            print("=" * 80)
            
            # Mostrar resumen si existe
            if transcript.get('summary'):
                summary = transcript['summary']
                print(f"\n📊 RESUMEN:")
                if summary.get('overview'):
                    print(f"   {summary['overview']}")
                if summary.get('keywords'):
                    print(f"\n🏷️  Keywords: {', '.join(summary['keywords'])}")
                if summary.get('action_items'):
                    print(f"\n✅ Action Items:")
                    for item in summary['action_items']:
                        print(f"   - {item}")
            
            return
        
        if attempt < max_attempts:
            print(f"   ⏳ Aún procesando... esperando {wait_time}s")
            time.sleep(wait_time)
    
    print(f"\n⏱️  Timeout: La transcripción está tomando más tiempo del esperado")
    print(f"   Puedes consultar manualmente con el Transcript ID: {transcript_id}")

if __name__ == "__main__":
    main()

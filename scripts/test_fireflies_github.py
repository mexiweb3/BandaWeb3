#!/usr/bin/env python3
"""
Script para transcribir con Fireflies usando URLs de GitHub
"""
import os
import requests
import json
from pathlib import Path
import time

# Configuración
ENV_FILE = Path(".env")
GITHUB_REPO = "mexiweb3/BandaWeb3"
GITHUB_BRANCH = "master"  # Rama del repositorio
AUDIO_PATH = "shared/audio"
TEST_FILE = "1kvJpbwePbwKE.mp3"
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"

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

def get_github_raw_url(filename):
    """
    Genera la URL raw de GitHub para un archivo
    
    Args:
        filename: Nombre del archivo MP3
    
    Returns:
        str: URL HTTPS del archivo en GitHub
    """
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{AUDIO_PATH}/{filename}"
    return url

def verify_url_accessible(url):
    """Verifica que la URL sea accesible"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except:
        return False

def upload_audio_to_fireflies(audio_url, title, api_key, language='es'):
    """Sube un archivo de audio a Fireflies para transcripción"""
    
    mutation = """
    mutation UploadAudio($input: AudioUploadInput!) {
        uploadAudio(input: $input) {
            success
            title
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
    print(f"   URL: {audio_url}")
    print(f"   Título: {title}")
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"❌ Error en GraphQL:")
                for error in result['errors']:
                    print(f"   {error.get('message', 'Unknown error')}")
                return None
            return result.get('data', {}).get('uploadAudio', {})
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def find_transcript_by_title(title, api_key):
    """Busca un transcript por título"""
    
    query = """
    query Transcripts {
        transcripts {
            id
            title
            date
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
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                return None
            
            transcripts = result.get('data', {}).get('transcripts', [])
            # Buscar por título
            for t in transcripts:
                if title in t.get('title', ''):
                    return t.get('id')
            return None
        else:
            return None
    except Exception as e:
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
                return None
            return result.get('data', {}).get('transcript', {})
        else:
            return None
    except Exception as e:
        return None

def main():
    print("=" * 80)
    print("FIREFLIES.AI - TRANSCRIPCIÓN CON GITHUB URLs")
    print("=" * 80)
    print()
    
    # Verificar API key
    api_key = load_fireflies_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Por favor configura tu FIREFLIES_API_KEY en el archivo .env")
        return
    
    # Generar URL de GitHub
    github_url = get_github_raw_url(TEST_FILE)
    
    print(f"📁 Archivo: {TEST_FILE}")
    print(f"🌐 URL de GitHub: {github_url}")
    print()
    
    # Verificar que la URL sea accesible
    print("🔍 Verificando accesibilidad de la URL...")
    if not verify_url_accessible(github_url):
        print("❌ La URL no es accesible públicamente")
        print()
        print("Posibles razones:")
        print("1. El archivo no está en el repositorio de GitHub")
        print("2. El repositorio es privado")
        print("3. La rama o ruta es incorrecta")
        print()
        print("Soluciones:")
        print("1. Asegúrate de que los archivos MP3 estén en GitHub")
        print("2. Haz el repositorio público")
        print("3. O usa GitHub LFS para archivos grandes")
        return
    
    print("✅ URL accesible")
    print()
    
    # Enviar a Fireflies
    result = upload_audio_to_fireflies(
        audio_url=github_url,
        title="BandaWeb3 #002 - Prueba Fireflies (GitHub)",
        api_key=api_key,
        language='es'
    )
    
    if not result:
        return
    
    if not result.get('success'):
        print(f"❌ Error: {result.get('message', 'Unknown')}")
        return
    
    print(f"\n✅ Audio enviado exitosamente!")
    print(f"   Título: {result.get('title')}")
    print(f"   Mensaje: {result.get('message', 'N/A')}")
    print()
    print("⏳ Esperando procesamiento (esto puede tomar varios minutos)...")
    print("   Fireflies procesará el audio y generará la transcripción")
    print()
    
    # Esperar un poco antes de buscar el transcript
    time.sleep(30)
    
    # Buscar el transcript por título
    title_to_search = "BandaWeb3 #002 - Prueba Fireflies (GitHub)"
    transcript_id = None
    
    for attempt in range(1, 10):
        print(f"🔍 Buscando transcript (intento {attempt}/10)...")
        transcript_id = find_transcript_by_title(title_to_search, api_key)
        if transcript_id:
            print(f"✅ Transcript encontrado: {transcript_id}")
            break
        time.sleep(10)
    
    if not transcript_id:
        print("❌ No se pudo encontrar el transcript")
        print("   Revisa manualmente en: https://app.fireflies.ai/")
        return
    
    # Esperar y obtener transcripción
    max_attempts = 30
    wait_time = 20  # segundos entre intentos
    
    for attempt in range(1, max_attempts + 1):
        print(f"🔍 Intento {attempt}/{max_attempts} - Consultando transcripción...")
        
        transcript = get_transcript(transcript_id, api_key)
        
        if transcript and transcript.get('sentences'):
            print(f"\n✅ ¡Transcripción completada!")
            print(f"   Duración: {transcript.get('duration', 'N/A')} segundos")
            print(f"   Participantes: {len(transcript.get('participants', []))}")
            print(f"   Oraciones: {len(transcript.get('sentences', []))}")
            
            # Guardar resultado
            output_dir = Path("shared/transcriptions_fireflies")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{TEST_FILE.replace('.mp3', '')}_fireflies.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Transcripción guardada: {output_path}")
            
            # Mostrar muestra
            print(f"\n📝 Muestra de la transcripción:")
            print("=" * 80)
            for i, sentence in enumerate(transcript.get('sentences', [])[:10]):
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
                    print(f"\n🏷️  Keywords: {', '.join(summary['keywords'][:10])}")
                if summary.get('action_items'):
                    print(f"\n✅ Action Items:")
                    for item in summary['action_items'][:5]:
                        print(f"   - {item}")
            
            return
        
        if attempt < max_attempts:
            print(f"   ⏳ Aún procesando... esperando {wait_time}s")
            time.sleep(wait_time)
    
    print(f"\n⏱️  Timeout: La transcripción está tomando más tiempo del esperado")
    print(f"   Puedes consultar manualmente en: https://app.fireflies.ai/")
    print(f"   Transcript ID: {transcript_id}")

if __name__ == "__main__":
    main()

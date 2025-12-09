#!/usr/bin/env python3
"""
Script de prueba para transcribir con Fireflies.ai API
Nota: Fireflies requiere que los archivos estén accesibles vía HTTPS URL
"""
import os
import requests
import json
from pathlib import Path
import time

# Configuración
ENV_FILE = Path(".env")
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

def upload_audio_to_fireflies(audio_url, title, api_key, language='es'):
    """
    Sube un archivo de audio a Fireflies para transcripción
    
    Args:
        audio_url: URL HTTPS del archivo de audio (debe ser accesible públicamente)
        title: Título del episodio
        api_key: API key de Fireflies
        language: Código de idioma (default: 'es' para español)
    
    Returns:
        dict: Respuesta de la API con el transcript_id
    """
    
    # Mutation de GraphQL para subir audio
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
    
    # Variables para la mutation
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
    
    print(f"🚀 Enviando a Fireflies: {title}")
    print(f"   URL: {audio_url}")
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                print(f"❌ Error en GraphQL: {result['errors']}")
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
    """
    Obtiene la transcripción de Fireflies
    
    Args:
        transcript_id: ID de la transcripción
        api_key: API key de Fireflies
    
    Returns:
        dict: Datos de la transcripción
    """
    
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
                email
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
                print(f"❌ Error en GraphQL: {result['errors']}")
                return None
            return result.get('data', {}).get('transcript', {})
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """
    Ejemplo de uso de Fireflies API
    
    IMPORTANTE: Fireflies requiere que los archivos de audio estén accesibles
    vía HTTPS URL. No puedes subir archivos locales directamente.
    
    Opciones:
    1. Usar un servicio de almacenamiento (S3, Google Cloud Storage, etc.)
    2. Usar un servidor web temporal
    3. Usar URLs de archivos ya públicos
    """
    
    api_key = load_fireflies_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Por favor configura tu FIREFLIES_API_KEY en el archivo .env")
        print("\nPara obtener tu API key:")
        print("1. Ve a https://app.fireflies.ai/")
        print("2. Settings > Integrations > API")
        print("3. Copia tu API key")
        return
    
    print("=" * 80)
    print("FIREFLIES.AI API - PRUEBA DE TRANSCRIPCIÓN")
    print("=" * 80)
    print()
    
    # Ejemplo de uso
    print("⚠️  NOTA IMPORTANTE:")
    print("Fireflies requiere que los archivos estén accesibles vía HTTPS URL")
    print("No puedes subir archivos locales directamente.")
    print()
    print("Opciones para hacer tus archivos accesibles:")
    print("1. Subir a S3/Google Cloud Storage y generar URL firmada")
    print("2. Usar un servidor web temporal (ngrok, etc.)")
    print("3. Usar URLs de archivos ya públicos")
    print()
    
    # Ejemplo con URL pública (necesitarías reemplazar con tu URL real)
    example_url = "https://ejemplo.com/audio/episodio.mp3"
    example_title = "BandaWeb3 #002 - Prueba Fireflies"
    
    print(f"Ejemplo de uso:")
    print(f"  audio_url = '{example_url}'")
    print(f"  title = '{example_title}'")
    print()
    print("Para probar, descomenta las siguientes líneas y proporciona una URL válida:")
    print()
    print("# result = upload_audio_to_fireflies(")
    print("#     audio_url='TU_URL_HTTPS_AQUI',")
    print("#     title='BandaWeb3 #002',")
    print("#     api_key=api_key,")
    print("#     language='es'")
    print("# )")
    print("# ")
    print("# if result and result.get('success'):")
    print("#     transcript_id = result.get('transcript_id')")
    print("#     print(f'✅ Audio subido exitosamente!')")
    print("#     print(f'   Transcript ID: {transcript_id}')")
    print("#     print(f'   Esperando procesamiento...')")
    print("#     ")
    print("#     # Esperar y obtener transcripción")
    print("#     time.sleep(60)  # Esperar 1 minuto")
    print("#     transcript = get_transcript(transcript_id, api_key)")
    print("#     if transcript:")
    print("#         print('✅ Transcripción obtenida!')")
    print("#         print(json.dumps(transcript, indent=2))")

if __name__ == "__main__":
    main()

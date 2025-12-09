#!/usr/bin/env python3
"""
Script simplificado para probar Fireflies.ai
Usa un servidor HTTP local + SSH tunnel
"""
import os
import requests
import json
from pathlib import Path
import time
import subprocess
import threading

# Configuración
ENV_FILE = Path(".env")
AUDIO_DIR = Path("shared/audio")
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

def main():
    print("=" * 80)
    print("FIREFLIES.AI - PRUEBA SIMPLIFICADA")
    print("=" * 80)
    print()
    
    api_key = load_fireflies_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ API key no configurada")
        return
    
    print("⚠️  LIMITACIÓN: Fireflies requiere URLs HTTPS públicas")
    print()
    print("Para probar Fireflies necesitas:")
    print("1. Subir el archivo a un servidor web accesible")
    print("2. O usar un servicio de túnel (ngrok, localhost.run)")
    print()
    print("Ejemplo de URL que funcionaría:")
    print("  https://ejemplo.com/audio/1kvJpbwePbwKE.mp3")
    print()
    
    # Permitir al usuario ingresar una URL manualmente
    print("Si ya tienes una URL pública del archivo, ingrésala aquí:")
    print("(o presiona Enter para salir)")
    audio_url = input("URL: ").strip()
    
    if not audio_url:
        print("\n💡 Sugerencia: Usa Deepgram que acepta archivos locales directamente")
        return
    
    # Validar que sea HTTPS
    if not audio_url.startswith('https://'):
        print("❌ La URL debe ser HTTPS")
        return
    
    # Enviar a Fireflies
    result = upload_audio_to_fireflies(
        audio_url=audio_url,
        title="BandaWeb3 #002 - Prueba Fireflies",
        api_key=api_key,
        language='es'
    )
    
    if not result:
        return
    
    if not result.get('success'):
        print(f"❌ Error: {result.get('message', 'Unknown')}")
        return
    
    transcript_id = result.get('transcript_id')
    print(f"\n✅ Audio enviado!")
    print(f"   Transcript ID: {transcript_id}")
    print(f"\n⏳ Fireflies está procesando el audio...")
    print(f"   Puedes consultar el estado en: https://app.fireflies.ai/")
    print(f"   O esperar aquí (esto puede tomar varios minutos)")

if __name__ == "__main__":
    main()

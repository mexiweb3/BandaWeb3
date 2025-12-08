#!/usr/bin/env python3
import os
import requests
import json
from pathlib import Path

# Configuración
AUDIO_DIR = Path("shared/audio")
TRANSCRIPT_DIR = Path("shared/transcriptions")
ENV_FILE = Path(".env")

def load_api_key():
    """Carga la API key desde el archivo .env sin dependencias externas"""
    if not ENV_FILE.exists():
        print("❌ Error: No se encontró el archivo .env")
        return None
    
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                if key == 'DEEPGRAM_API_KEY':
                    return value.strip()
    return None

def transcribe_file(filepath, api_key):
    """Transcribe un archivo de audio usando Deepgram API"""
    url = "https://api.deepgram.com/v1/listen?model=nova-2&language=es&smart_format=true"
    
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/mp3"
    }

    print(f"🚀 Enviando a Deepgram: {filepath.name}...")
    
    try:
        with open(filepath, 'rb') as audio:
            response = requests.post(url, headers=headers, data=audio)
            
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    api_key = load_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Por favor configura tu DEEPGRAM_API_KEY en el archivo .env")
        return

    # Crear directorio de transcripciones si no existe
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    # Buscar archivos MP3
    mp3_files = list(AUDIO_DIR.glob("*.mp3"))
    print(f"📊 Encontrados {len(mp3_files)} archivos de audio.")

    for mp3_path in mp3_files:
        json_output_path = TRANSCRIPT_DIR / f"{mp3_path.stem}.json"
        
        if json_output_path.exists():
            print(f"⏭️  Ya existe transcripción para: {mp3_path.name}")
            continue
            
        print(f"\n🎙️  Procesando: {mp3_path.name} (Tamaño: {mp3_path.stat().st_size / (1024*1024):.2f} MB)")
        
        result = transcribe_file(mp3_path, api_key)
        
        if result:
            # Guardar JSON completo
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # Guardar texto plano también para lectura fácil
            txt_output_path = TRANSCRIPT_DIR / f"{mp3_path.stem}.txt"
            transcript_text = result.get('results', {}).get('channels', [])[0].get('alternatives', [])[0].get('transcript', '')
            
            with open(txt_output_path, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
                
            print(f"✅ Transcripción guardada: {json_output_path.name}")
        
    print("\n✨ Proceso completado.")

if __name__ == "__main__":
    main()

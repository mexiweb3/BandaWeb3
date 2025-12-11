#!/usr/bin/env python3
"""
Script para transcribir TODOS los episodios con Fireflies usando URLs de GitHub
"""
import os
import requests
import json
from pathlib import Path
import time

# Configuración
ENV_FILE = Path(".env")
GITHUB_REPO = "mexiweb3/BandaWeb3"
GITHUB_BRANCH = "master"
AUDIO_PATH = "shared/audio"
AUDIO_DIR = Path("shared/audio")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"
OUTPUT_DIR = Path("shared/transcriptions_fireflies")

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

def load_episode_metadata(space_id):
    """Carga metadata del episodio desde la base de datos"""
    import json
    from pathlib import Path
    
    db_paths = [
        Path("shared/episodes_database.json"),
        Path("shared/consolidated_database.json")
    ]
    
    for db_path in db_paths:
        if not db_path.exists():
            continue
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            episodes = data.get('episodes', [])
            for episode in episodes:
                space_url = episode.get('space_url', '')
                if space_id in space_url:
                    return episode
        except Exception as e:
            pass
    
    return None

def get_github_raw_url(filename):
    """Genera la URL raw de GitHub para un archivo"""
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{AUDIO_PATH}/{filename}"
    return url

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
    
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'errors' in result:
                return None
            return result.get('data', {}).get('uploadAudio', {})
        else:
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    print("=" * 80)
    print("FIREFLIES.AI - TRANSCRIPCIÓN MASIVA DE EPISODIOS")
    print("=" * 80)
    print()
    
    # Verificar API key
    api_key = load_fireflies_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Por favor configura tu FIREFLIES_API_KEY en el archivo .env")
        return
    
    # Crear directorio de salida
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Obtener lista de archivos MP3
    mp3_files = sorted(AUDIO_DIR.glob("*.mp3"))
    total_files = len(mp3_files)
    
    print(f"📁 Encontrados {total_files} archivos de audio")
    print(f"🌐 Repositorio: {GITHUB_REPO}")
    print(f"📂 Salida: {OUTPUT_DIR}")
    print()
    
    # Contador de éxitos y fallos
    uploaded = 0
    failed = 0
    skipped = 0
    
    for i, mp3_path in enumerate(mp3_files, 1):
        filename = mp3_path.name
        space_id = mp3_path.stem
        
        # Verificar si ya existe el registro de subida
        output_file = OUTPUT_DIR / f"{space_id}_upload_record.json"
        if output_file.exists():
            print(f"[{i}/{total_files}] ⏭️  Ya existe: {filename}")
            skipped += 1
            continue
        
        # Cargar metadata del episodio
        episode = load_episode_metadata(space_id)
        if episode:
            title = f"BandaWeb3 - {episode.get('title', filename)}"
            episode_num = episode.get('number', 'N/A')
        else:
            title = f"BandaWeb3 - {filename}"
            episode_num = "N/A"
        
        # Generar URL de GitHub
        github_url = get_github_raw_url(filename)
        
        print(f"[{i}/{total_files}] 🔥 Subiendo: {filename}")
        print(f"            Episodio: #{episode_num}")
        print(f"            Título: {title[:60]}...")
        
        # Subir a Fireflies
        result = upload_audio_to_fireflies(
            audio_url=github_url,
            title=title,
            api_key=api_key,
            language='es'
        )
        
        if result and result.get('success'):
            print(f"            ✅ {result.get('message', 'Uploaded')}")
            uploaded += 1
            
            # Guardar registro de subida
            upload_record = {
                "filename": filename,
                "space_id": space_id,
                "title": title,
                "github_url": github_url,
                "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "queued"
            }
            
            record_file = OUTPUT_DIR / f"{space_id}_upload_record.json"
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(upload_record, f, indent=2, ensure_ascii=False)
        else:
            print(f"            ❌ Error al subir")
            failed += 1
        
        # Pequeña pausa para no saturar la API
        time.sleep(2)
        print()
    
    print("=" * 80)
    print("📊 RESUMEN DE SUBIDA")
    print("=" * 80)
    print(f"✅ Subidos exitosamente: {uploaded}")
    print(f"⏭️  Ya existían: {skipped}")
    print(f"❌ Fallidos: {failed}")
    print(f"📁 Total procesados: {i}/{total_files}")
    print()
    print("⏳ Los archivos están en cola de procesamiento en Fireflies")
    print("   Puedes revisar el progreso en: https://app.fireflies.ai/")
    print()
    print("💡 Para descargar las transcripciones cuando estén listas:")
    print("   python3 scripts/download_fireflies_transcripts.py")

if __name__ == "__main__":
    main()

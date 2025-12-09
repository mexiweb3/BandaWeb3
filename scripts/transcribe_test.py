#!/usr/bin/env python3
"""Script temporal para transcribir solo el episodio de prueba"""
import sys
import os

# Agregar el directorio de scripts al path
sys.path.insert(0, 'scripts')

# Importar funciones del script principal
from pathlib import Path
import json
from transcribe_deepgram import load_api_key, transcribe_file, generate_formatted_transcript

# Configuración
AUDIO_DIR = Path("shared/audio")
TRANSCRIPT_DIR = Path("shared/transcriptions")
TEST_FILE = "1kvJpbwePbwKE.mp3"

def main():
    api_key = load_api_key()
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ Por favor configura tu DEEPGRAM_API_KEY en el archivo .env")
        return

    # Crear directorio de transcripciones si no existe
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    # Procesar solo el archivo de prueba
    mp3_path = AUDIO_DIR / TEST_FILE
    
    if not mp3_path.exists():
        print(f"❌ No se encontró el archivo: {TEST_FILE}")
        return
    
    print(f"🎙️  Procesando: {mp3_path.name} (Tamaño: {mp3_path.stat().st_size / (1024*1024):.2f} MB)")
    
    result = transcribe_file(mp3_path, api_key)
    
    if result:
        # 1. Guardar JSON completo
        json_output_path = TRANSCRIPT_DIR / f"{mp3_path.stem}.json"
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"   ✅ JSON completo: {json_output_path.name}")
        
        # 2. Guardar transcripción formateada
        txt_output_path = TRANSCRIPT_DIR / f"{mp3_path.stem}.txt"
        formatted_text = generate_formatted_transcript(result, space_id=mp3_path.stem)
        with open(txt_output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        print(f"   ✅ Transcripción TXT: {txt_output_path.name}")
        
        # Mostrar estadísticas
        if 'results' in result and 'utterances' in result['results']:
            num_speakers = len(set(u.get('speaker', 0) for u in result['results']['utterances']))
            num_utterances = len(result['results']['utterances'])
            print(f"   📊 {num_speakers} hablantes detectados, {num_utterances} segmentos")
    
    print("\n✨ Proceso completado.")

if __name__ == "__main__":
    main()

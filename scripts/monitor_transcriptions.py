#!/usr/bin/env python3
"""
Script para monitorear el progreso de transcripciones
"""
import time
import subprocess
from pathlib import Path

def check_deepgram_progress():
    """Verifica el progreso de Deepgram"""
    transcriptions_dir = Path("shared/transcriptions")
    json_files = list(transcriptions_dir.glob("*.json"))
    txt_files = list(transcriptions_dir.glob("*.txt"))
    
    # Total esperado
    audio_dir = Path("shared/audio")
    total_mp3 = len(list(audio_dir.glob("*.mp3")))
    
    return len(json_files), total_mp3

def check_fireflies_progress():
    """Verifica si Fireflies terminó"""
    fireflies_dir = Path("shared/transcriptions_fireflies")
    if not fireflies_dir.exists():
        return False
    
    json_files = list(fireflies_dir.glob("*_fireflies.json"))
    return len(json_files) > 0

def check_deepgram_process():
    """Verifica si el proceso de Deepgram sigue corriendo"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        return 'transcribe_deepgram.py' in result.stdout
    except:
        return False

def check_fireflies_process():
    """Verifica si el proceso de Fireflies sigue corriendo"""
    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        return 'test_fireflies_github.py' in result.stdout
    except:
        return False

def main():
    print("🔍 Monitoreando procesos de transcripción...")
    print()
    
    deepgram_done = False
    fireflies_done = False
    
    while not (deepgram_done and fireflies_done):
        # Verificar Deepgram
        completed, total = check_deepgram_progress()
        deepgram_running = check_deepgram_process()
        
        if completed == total and not deepgram_running:
            if not deepgram_done:
                print(f"✅ Deepgram completado: {completed}/{total} episodios")
                deepgram_done = True
        else:
            print(f"⏳ Deepgram: {completed}/{total} episodios ({completed*100//total if total > 0 else 0}%)")
        
        # Verificar Fireflies
        fireflies_completed = check_fireflies_progress()
        fireflies_running = check_fireflies_process()
        
        if fireflies_completed and not fireflies_running:
            if not fireflies_done:
                print(f"✅ Fireflies completado: Episodio #002 transcrito")
                fireflies_done = True
        else:
            status = "Procesando..." if fireflies_running else "Esperando..."
            print(f"⏳ Fireflies: {status}")
        
        print()
        
        if deepgram_done and fireflies_done:
            break
        
        # Esperar 30 segundos antes de verificar de nuevo
        time.sleep(30)
    
    print("=" * 80)
    print("🎉 ¡TODOS LOS PROCESOS COMPLETADOS!")
    print("=" * 80)
    print()
    print("📊 Resumen:")
    print(f"   Deepgram: {completed}/{total} episodios")
    print(f"   Fireflies: 1 episodio (#002)")
    print()
    print("📁 Ubicaciones:")
    print(f"   Deepgram: shared/transcriptions/")
    print(f"   Fireflies: shared/transcriptions_fireflies/")

if __name__ == "__main__":
    main()

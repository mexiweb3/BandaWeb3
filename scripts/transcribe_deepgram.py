#!/usr/bin/env python3
import os
import requests
import json
from pathlib import Path
from datetime import timedelta

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

def load_episode_metadata(space_id):
    """Carga metadata del episodio desde la base de datos"""
    import json
    from pathlib import Path
    
    # Intentar primero con episodes_database.json
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
            
            # Buscar episodio por space_id en space_url
            episodes = data.get('episodes', [])
            for episode in episodes:
                space_url = episode.get('space_url') or ''
                if space_id in space_url:
                    return episode
        except Exception as e:
            print(f"⚠️  Error cargando {db_path.name}: {e}")
    
    return None

def format_episode_header(episode):
    """Formatea el header con información del episodio"""
    if not episode:
        return ""
    
    lines = []
    lines.append("=" * 80)
    lines.append("INFORMACIÓN DEL EPISODIO")
    lines.append("=" * 80)
    
    # Información básica
    if episode.get('number'):
        lines.append(f"Episodio: #{episode['number']}")
    if episode.get('title'):
        lines.append(f"Título: {episode['title']}")
    if episode.get('date'):
        lines.append(f"Fecha: {episode['date']}")
    if episode.get('time'):
        lines.append(f"Hora: {episode['time']}")
    
    # Host y tipo
    if episode.get('host'):
        lines.append(f"Host: {episode['host']}")
    if episode.get('type'):
        lines.append(f"Tipo: {episode['type']}")
    
    # Co-hosts si existen
    if episode.get('cohosts'):
        cohosts_str = ', '.join(episode['cohosts'])
        lines.append(f"Co-hosts: {cohosts_str}")
    
    # Invitados
    if episode.get('guests'):
        guests_str = ', '.join(episode['guests'])
        lines.append(f"Invitados: {guests_str}")
    
    # Descripción
    if episode.get('description'):
        lines.append(f"\nDescripción:")
        lines.append(episode['description'])
    
    # Temas
    if episode.get('topics'):
        topics_str = ', '.join(episode['topics'])
        lines.append(f"\nTemas: {topics_str}")
    
    # Estadísticas
    if episode.get('duration'):
        lines.append(f"\nDuración: {episode['duration']}")
    if episode.get('listeners'):
        lines.append(f"Escuchas: {episode['listeners']}")
    if episode.get('speakers'):
        lines.append(f"Speakers: {episode['speakers']}")
    
    # Links
    lines.append("\nLinks:")
    if episode.get('space_url'):
        lines.append(f"  Space: {episode['space_url']}")
    if episode.get('spacesdashboard_url'):
        lines.append(f"  Dashboard: {episode['spacesdashboard_url']}")
    if episode.get('unlock_url'):
        lines.append(f"  Unlock: {episode['unlock_url']}")
    if episode.get('opensea_url'):
        lines.append(f"  OpenSea: {episode['opensea_url']}")
    if episode.get('contract_url'):
        lines.append(f"  Contract: {episode['contract_url']}")
    
    # Links de invitados
    if episode.get('guest_links'):
        lines.append("\nRedes de invitados:")
        for guest, link in episode['guest_links'].items():
            lines.append(f"  {guest}: {link}")
    
    lines.append("\n" + "=" * 80)
    lines.append("TRANSCRIPCIÓN")
    lines.append("=" * 80 + "\n")
    
    return "\n".join(lines)

def format_timestamp(seconds):
    """Convierte segundos a formato HH:MM:SS"""
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def transcribe_file(filepath, api_key):
    """Transcribe un archivo de audio usando Deepgram API con características avanzadas"""
    # URL con todas las características habilitadas
    # Nota: summarize no está disponible para español
    url = (
        "https://api.deepgram.com/v1/listen?"
        "model=nova-2&"
        "language=es&"
        "smart_format=true&"
        "diarize=true&"           # Identificación de hablantes
        "paragraphs=true&"         # Agrupación en párrafos
        "utterances=true&"         # Segmentos por hablante
        "punctuate=true&"          # Puntuación mejorada
        "filler_words=true"        # Detecta muletillas
    )
    
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

def generate_formatted_transcript(result, space_id=None):
    """Genera transcripción formateada con hablantes y timestamps"""
    formatted_lines = []
    
    # Agregar información del episodio si está disponible
    if space_id:
        episode = load_episode_metadata(space_id)
        if episode:
            header = format_episode_header(episode)
            formatted_lines.append(header)
    
    # Agregar resumen si está disponible
    if 'results' in result and 'summary' in result['results']:
        summary = result['results']['summary']
        if summary and 'short' in summary:
            formatted_lines.append("=" * 80)
            formatted_lines.append("RESUMEN")
            formatted_lines.append("=" * 80)
            formatted_lines.append(summary['short'])
            formatted_lines.append("\n" + "=" * 80)
            formatted_lines.append("TRANSCRIPCIÓN COMPLETA")
            formatted_lines.append("=" * 80 + "\n")
    
    # Obtener utterances (segmentos por hablante)
    if 'results' in result and 'utterances' in result['results']:
        utterances = result['results']['utterances']
        
        # Agrupar utterances consecutivos del mismo hablante
        grouped_utterances = []
        current_group = None
        
        for utt in utterances:
            speaker = utt.get('speaker', 0)
            start = utt.get('start', 0)
            end = utt.get('end', 0)
            text = utt.get('transcript', '').strip()
            confidence = utt.get('confidence', 0)
            
            if not text:  # Saltar utterances vacíos
                continue
            
            # Si es el mismo hablante, agregar al grupo actual
            if current_group and current_group['speaker'] == speaker:
                current_group['texts'].append(text)
                current_group['confidences'].append(confidence)
                current_group['timestamps'].append((start, end))
                current_group['end'] = end
            else:
                # Guardar el grupo anterior si existe
                if current_group:
                    grouped_utterances.append(current_group)
                
                # Crear nuevo grupo
                current_group = {
                    'speaker': speaker,
                    'start': start,
                    'end': end,
                    'texts': [text],
                    'confidences': [confidence],
                    'timestamps': [(start, end)]
                }
        
        # Agregar el último grupo
        if current_group:
            grouped_utterances.append(current_group)
        
        # Formatear los grupos, dividiendo si son muy largos
        for group in grouped_utterances:
            speaker = group['speaker']
            start = group['start']
            end = group['end']
            texts = group['texts']
            timestamps = group['timestamps']
            avg_confidence = sum(group['confidences']) / len(group['confidences'])
            
            # Unir todos los textos
            combined_text = ' '.join(texts)
            
            # Si el segmento dura más de 60 segundos, dividirlo en párrafos
            duration = end - start
            if duration > 60:
                # Dividir por oraciones (puntos, signos de interrogación, exclamación)
                import re
                sentences = re.split(r'([.!?]\s+)', combined_text)
                
                # Reconstruir oraciones con sus puntuaciones
                full_sentences = []
                for i in range(0, len(sentences)-1, 2):
                    if i+1 < len(sentences):
                        full_sentences.append(sentences[i] + sentences[i+1])
                    else:
                        full_sentences.append(sentences[i])
                if len(sentences) % 2 == 1:
                    full_sentences.append(sentences[-1])
                
                # Agrupar oraciones en chunks de ~60 segundos
                chunks = []
                current_chunk = []
                chunk_start_time = start
                time_per_char = duration / len(combined_text) if combined_text else 0
                
                current_chars = 0
                for sentence in full_sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    sentence_chars = len(sentence)
                    sentence_duration = sentence_chars * time_per_char
                    
                    # Si agregar esta oración excede 60s, crear nuevo chunk
                    if current_chunk and (current_chars * time_per_char) > 60:
                        chunk_text = ' '.join(current_chunk)
                        chunk_end_time = chunk_start_time + (current_chars * time_per_char)
                        chunks.append((chunk_start_time, chunk_end_time, chunk_text))
                        
                        current_chunk = [sentence]
                        chunk_start_time = chunk_end_time
                        current_chars = sentence_chars
                    else:
                        current_chunk.append(sentence)
                        current_chars += sentence_chars
                
                # Agregar el último chunk
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append((chunk_start_time, end, chunk_text))
                
                # Formatear cada chunk
                for chunk_start, chunk_end, chunk_text in chunks:
                    timestamp = format_timestamp(chunk_start)
                    formatted_lines.append(f"\n[Speaker {speaker} - {timestamp}]")
                    formatted_lines.append(chunk_text)
            else:
                # Segmento corto, no dividir
                timestamp = format_timestamp(start)
                formatted_lines.append(f"\n[Speaker {speaker} - {timestamp}]")
                formatted_lines.append(combined_text)
    
    # Si no hay utterances, usar párrafos
    elif 'results' in result and 'channels' in result['results']:
        channels = result['results']['channels']
        if channels and 'alternatives' in channels[0]:
            alternatives = channels[0]['alternatives']
            if alternatives and 'paragraphs' in alternatives[0]:
                paragraphs = alternatives[0]['paragraphs']
                if 'paragraphs' in paragraphs:
                    for para in paragraphs['paragraphs']:
                        formatted_lines.append("\n" + para.get('text', ''))
    
    return "\n".join(formatted_lines)



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
            # 1. Guardar JSON completo con toda la metadata
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"   ✅ JSON completo: {json_output_path.name}")
            
            # 2. Guardar transcripción formateada con hablantes
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

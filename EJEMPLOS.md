# Ejemplos de Uso - BandaWeb3 Automation

## 🎯 Caso de Uso 1: Procesar Episodio Completo (Método Más Fácil)

### Escenario:
Acabas de terminar tu Space del martes, episodio #075.

### Pasos:

**1. Descargar audio (5-15 minutos)**
```
1. Ir a: https://www.twitterspacegpt.com/downloaders
2. Pegar URL del Space: https://twitter.com/i/spaces/1ABC...
3. Ingresar tu email
4. Esperar correo con link de descarga
5. Descargar MP3
```

**2. Procesar todo automáticamente (8-10 minutos)**
```bash
cd bandaweb3-automation

# Un solo comando hace todo:
./scripts/process_episode.sh 075 ~/Downloads/space_audio.mp3

# Esto ejecuta automáticamente:
# ✓ Crea carpeta E075_2024-12-05
# ✓ Organiza archivos
# ✓ Transcribe con Whisper API
# ✓ Genera hilo, artículo, post LinkedIn, highlights
```

**3. Revisar y publicar (10-15 minutos)**
```bash
# Ver hilo de X
cat "../E075_2024-12-05/content/thread_x.json"

# Leer artículo
cat "../E075_2024-12-05/content/article.md"

# Ver highlights para videos
cat "../E075_2024-12-05/content/video_highlights.json"
```

**Total:** ~25-40 minutos (vs. varias horas manualmente)

---

## 🎯 Caso de Uso 2: Solo Transcripción Rápida

### Escenario:
Necesitas la transcripción urgente pero no el contenido todavía.

```bash
# Solo transcribir
python3 scripts/transcribe_audio.py ~/Downloads/space_audio.mp3

# Resultado en mismo directorio:
# - transcription.txt
# - transcription.json
# - transcription.srt

# Tiempo: 2-5 minutos
```

---

## 🎯 Caso de Uso 3: Solo Hilo de X (Para Publicar Rápido)

### Escenario:
Quieres publicar un hilo inmediatamente después del Space.

```bash
# 1. Descargar y organizar
mkdir -p ../E075_2024-12-05/raw
mv ~/Downloads/space_audio.mp3 ../E075_2024-12-05/raw/audio.mp3

# 2. Transcribir
python3 scripts/transcribe_audio.py ../E075_2024-12-05/raw/audio.mp3

# 3. Generar SOLO hilo
python3 scripts/generate_content.py ../E075_2024-12-05 -t thread

# 4. Ver resultado
cat ../E075_2024-12-05/content/thread_x.json

# Tiempo total: ~5-7 minutos
```

---

## 🎯 Caso de Uso 4: Procesar Episodios Viejos en Batch

### Escenario:
Tienes los MP3 de episodios #073 y #074 y quieres procesarlos.

```bash
# Procesar episodio 073
./scripts/process_episode.sh 073 "../073/BandaWeb3 #073 Open 🎙️ @EFDevcon 🇦🇷.mp3" --date 2024-12-03

# Procesar episodio 074
./scripts/process_episode.sh 074 "../074 Devconnect Parte 2/BandaWeb3 #074 Hackathon @ETHGlobal 🇦🇷 EVVM.mp3" --date 2024-12-04

# Ambos se procesarán en paralelo si los ejecutas en terminales separadas
```

---

## 🎯 Caso de Uso 5: Generar Solo Video Highlights

### Escenario:
Ya tienes transcripción y contenido, pero quieres identificar momentos para videos.

```bash
# Generar solo highlights
python3 scripts/generate_content.py ../E075_2024-12-05 -t highlights

# Ver resultado
cat ../E075_2024-12-05/content/video_highlights.json
```

**Ejemplo de salida:**
```json
{
  "highlights": [
    {
      "title": "Qué es EVVM explicado simple",
      "start_time": "05:30",
      "end_time": "06:15",
      "duration_seconds": 45,
      "transcript": "...",
      "speaker": "Germán",
      "reason": "Explicación clara de concepto técnico complejo",
      "potential_reach": "high"
    },
    ...
  ]
}
```

---

## 🎯 Caso de Uso 6: Workflow Semanal Completo

### Escenario:
Tu rutina típica semanal con 2 Spaces.

**Martes (Space #075):**

```bash
# Durante el Space: Tomar notas mentales de momentos destacados

# Después del Space (15 min):
# 1. Iniciar descarga en TwitterSpaceGPT
# 2. Mientras esperas, preparar carpeta
mkdir -p ../E075_$(date +%Y-%m-%d)/{raw,transcripts,content,media}

# 3. Cuando llegue el email, descargar
# 4. Procesar todo
./scripts/process_episode.sh 075 ~/Downloads/space_tuesday.mp3

# 5. Revisar hilo mientras tomas café
cat ../E075_*/content/thread_x.json

# 6. Publicar hilo en X
# (Copiar y pegar o usar herramienta de scheduling)
```

**Jueves (Space Expedito #076):**

```bash
# Mismo proceso
./scripts/process_episode.sh 076 ~/Downloads/space_thursday.mp3

# Generar solo thread para este (más informal)
python3 scripts/generate_content.py ../E076_* -t thread
```

**Fin de Semana (Contenido adicional):**

```bash
# Generar artículos largos de ambos episodios
for dir in ../E075_* ../E076_*; do
    python3 scripts/generate_content.py "$dir" -t article
done

# Crear videos de highlights
# (Próximamente con scripts de video)
```

---

## 🎯 Caso de Uso 7: Recuperar de Error

### Escenario:
La transcripción falló o quieres re-generar contenido.

**Re-transcribir:**
```bash
# Si la transcripción falló
python3 scripts/transcribe_audio.py ../E075_*/raw/audio.mp3 --output ../E075_*/transcripts
```

**Re-generar contenido:**
```bash
# Si no te gustó el contenido generado
# Solo regenerar hilo:
python3 scripts/generate_content.py ../E075_* -t thread

# Regenerar todo:
python3 scripts/generate_content.py ../E075_*
```

**Procesar sin transcribir de nuevo:**
```bash
# Si ya tienes la transcripción
./scripts/process_episode.sh 075 ~/Downloads/audio.mp3 --skip-transcription
```

---

## 🎯 Caso de Uso 8: Comprimir Audio Grande

### Escenario:
Tu archivo MP3 es >25MB y no puedes usar Whisper API.

```bash
# Comprimir audio a 128kbps
ffmpeg -i space_original.mp3 -b:a 128k space_comprimido.mp3

# Verificar tamaño
ls -lh space_comprimido.mp3

# Ahora transcribir
python3 scripts/transcribe_audio.py space_comprimido.mp3
```

---

## 📊 Comparación de Métodos

| Método | Tiempo | Complejidad | Cuando Usar |
|--------|--------|-------------|-------------|
| **Script automatizado** | 8-10 min | Baja | Proceso completo estándar |
| **Solo transcripción** | 2-5 min | Muy baja | Necesitas texto urgente |
| **Solo thread** | 5-7 min | Baja | Publicación rápida en X |
| **Paso por paso manual** | 10-15 min | Media | Aprendizaje o casos especiales |

---

## 💡 Tips y Mejores Prácticas

### Para Ahorrar Tiempo:

1. **Durante el Space:**
   - Anotar timestamps de momentos importantes manualmente
   - Pedir a invitados deletrear nombres complejos

2. **Inmediatamente después:**
   - Iniciar descarga en TwitterSpaceGPT
   - Mientras esperas, preparar carpetas

3. **Batch processing:**
   - Procesar múltiples episodios en paralelo
   - Generar todos los hilos juntos

### Para Ahorrar Dinero:

1. **Comprimir audio:**
   ```bash
   ffmpeg -i original.mp3 -b:a 96k comprimido.mp3
   ```
   - 96kbps es suficiente para voz
   - Reduce costos de Whisper API

2. **Generar selectivamente:**
   - Solo generar lo que necesites (`-t thread` vs `-t all`)
   - Artículos largos cuestan más tokens

3. **Revisar antes de regenerar:**
   - Editar manualmente en vez de regenerar
   - Un error pequeño no amerita gastar más API calls

### Para Mejorar Calidad:

1. **Transcripciones:**
   - Audio limpio = mejor resultado
   - Revisar nombres propios y corregir en JSON

2. **Contenido generado:**
   - Proporcionar contexto en metadata
   - Editar prompts según tu estilo

3. **Highlights para videos:**
   - Complementar con tus notas del Space
   - IA identifica momentos técnicos, tú conoces los virales

---

## 🔄 Workflow Recomendado Definitivo

```bash
# 1. Iniciar descarga (0 min de trabajo activo)
https://www.twitterspacegpt.com/downloaders

# 2. Preparar mientras esperas (1 min)
mkdir -p ../E$(next_episode)_$(date +%Y-%m-%d)/{raw,transcripts,content,media}

# 3. Cuando llegue email, descargar (30 seg)
# Click en link → Download

# 4. Procesar automáticamente (1 min de setup, 8-10 min procesando)
./scripts/process_episode.sh $(next_episode) ~/Downloads/space.mp3

# 5. Revisar mientras procesa (2 min)
# Leer notifications, responder DMs

# 6. Cuando termine, revisar contenido (10 min)
cat content/thread_x.json
cat content/article.md

# 7. Publicar (5 min)
# Copiar hilo a X
# Programar artículo

# TOTAL TIEMPO ACTIVO: ~20 minutos
# TOTAL TIEMPO REAL: ~30 minutos (incluyendo esperas)
```

---

**Documentación completa en:**
- [README.md](README.md) - Overview del sistema
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Guía de inicio
- [docs/DOWNLOAD_AUDIO.md](docs/DOWNLOAD_AUDIO.md) - Descarga de Spaces

---

**¿Dudas?** Experimenta con los ejemplos anteriores. El sistema está diseñado para ser flexible según tus necesidades.

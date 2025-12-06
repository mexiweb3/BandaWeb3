# Cómo Descargar Audio de Twitter Spaces

## Método Recomendado: TwitterSpaceGPT ⭐

**URL:** https://www.twitterspacegpt.com/downloaders

### ✅ Ventajas:
- Gratis y fácil de usar
- No requiere instalación
- Funciona con cualquier Space (no solo los tuyos)
- Recibes link de descarga por correo
- Audio en formato MP3 de buena calidad

### 📝 Proceso Paso a Paso:

1. **Ir al sitio:**
   ```
   https://www.twitterspacegpt.com/downloaders
   ```

2. **Pegar URL del Space:**
   - Copia el link de tu Space en X
   - Ejemplo: `https://twitter.com/i/spaces/1DXxyNABCDE123`
   - Pégalo en el formulario

3. **Ingresar tu email:**
   - Recibirás el link de descarga por correo
   - Tiempo de espera: 5-15 minutos (depende de la duración)

4. **Descargar MP3:**
   - Abre el correo
   - Click en el link de descarga
   - Guarda el archivo

5. **Organizar en carpeta:**
   ```bash
   # Crear carpeta del episodio
   mkdir -p "../E075_2024-12-05/raw"

   # Mover archivo descargado
   mv ~/Downloads/space_*.mp3 "../E075_2024-12-05/raw/audio.mp3"
   ```

---

## Workflow Completo con TwitterSpaceGPT

### Setup Inicial (Una sola vez)

```bash
cd bandaweb3-automation

# Instalar dependencias si aún no lo hiciste
pip install -r requirements.txt

# Configurar API keys
cp config/.env.example config/.env
nano config/.env  # Agregar tus API keys
```

### Para Cada Episodio Nuevo

#### 1. Durante/Después del Space

**a) Anotar información:**
- Número de episodio
- Fecha
- Invitados principales
- URL del Space

**b) Iniciar descarga:**
- Ir a https://www.twitterspacegpt.com/downloaders
- Pegar URL del Space
- Ingresar tu email
- Esperar correo (5-15 min)

#### 2. Preparar Estructura de Carpetas

```bash
# Ejemplo para episodio 075
EPISODE="075"
DATE=$(date +%Y-%m-%d)
EPISODE_DIR="../E${EPISODE}_${DATE}"

# Crear estructura
mkdir -p "$EPISODE_DIR"/{raw,transcripts,content,media}

echo "Carpeta creada: $EPISODE_DIR"
```

#### 3. Descargar y Mover Audio

```bash
# Descargar del link en el correo
# Luego mover a la carpeta correcta
mv ~/Downloads/space_*.mp3 "$EPISODE_DIR/raw/audio.mp3"

echo "✓ Audio guardado en: $EPISODE_DIR/raw/audio.mp3"
```

#### 4. Transcribir con Whisper API

```bash
# Usar Whisper API (cloud) - más rápido
python3 scripts/transcribe_audio.py "$EPISODE_DIR/raw/audio.mp3"

# Salida:
# - $EPISODE_DIR/transcripts/transcription.txt
# - $EPISODE_DIR/transcripts/transcription.json (con timestamps)
# - $EPISODE_DIR/transcripts/transcription.srt
```

**Tiempo estimado:** 2-5 minutos (para audio de 90 min)

#### 5. Generar Contenido con Claude

```bash
# Generar TODO el contenido
python3 scripts/generate_content.py "$EPISODE_DIR"

# O generar solo lo que necesites:
# Solo hilo de X:
python3 scripts/generate_content.py "$EPISODE_DIR" -t thread

# Solo highlights para videos:
python3 scripts/generate_content.py "$EPISODE_DIR" -t highlights
```

**Tiempo estimado:** 3-5 minutos

#### 6. Revisar y Publicar

```bash
# Ver hilo generado
cat "$EPISODE_DIR/content/thread_x.json"

# Ver artículo
cat "$EPISODE_DIR/content/article.md"

# Ver highlights para videos
cat "$EPISODE_DIR/content/video_highlights.json"
```

---

## Script de Automatización Todo-en-Uno

Crea este script para automatizar el proceso completo:

```bash
#!/bin/bash
# bandaweb3-automation/scripts/process_episode.sh

# Uso: ./scripts/process_episode.sh 075 /path/to/downloaded_audio.mp3

EPISODE=$1
AUDIO_FILE=$2
DATE=$(date +%Y-%m-%d)
EPISODE_DIR="../E${EPISODE}_${DATE}"

echo "=================================="
echo "Procesando Episodio #$EPISODE"
echo "=================================="

# 1. Crear estructura
echo "📁 Creando estructura de carpetas..."
mkdir -p "$EPISODE_DIR"/{raw,transcripts,content,media}

# 2. Mover audio
echo "🎵 Moviendo audio..."
cp "$AUDIO_FILE" "$EPISODE_DIR/raw/audio.mp3"

# 3. Transcribir
echo "📝 Transcribiendo (esto tomará unos minutos)..."
python3 scripts/transcribe_audio.py "$EPISODE_DIR/raw/audio.mp3"

# 4. Generar contenido
echo "✨ Generando contenido..."
python3 scripts/generate_content.py "$EPISODE_DIR"

# 5. Resumen
echo ""
echo "=================================="
echo "✅ COMPLETADO!"
echo "=================================="
echo "Archivos generados en: $EPISODE_DIR"
echo ""
echo "Próximos pasos:"
echo "1. Revisar transcripción: $EPISODE_DIR/transcripts/transcription.txt"
echo "2. Revisar hilo de X: $EPISODE_DIR/content/thread_x.json"
echo "3. Revisar artículo: $EPISODE_DIR/content/article.md"
echo "4. Revisar highlights: $EPISODE_DIR/content/video_highlights.json"
```

**Dar permisos de ejecución:**
```bash
chmod +x scripts/process_episode.sh
```

**Usar:**
```bash
./scripts/process_episode.sh 075 ~/Downloads/space_audio.mp3
```

---

## Métodos Alternativos (Backup)

### Método 2: Como Host del Space

Si eres el host, puedes descargar directamente desde X:

1. Ve a X (Twitter)
2. Abre tu Space completado
3. Click en "Download recording"
4. Disponible por 30 días

### Método 3: Herramientas de Línea de Comando

Para usuarios avanzados:

```bash
# Usando twitter-api-client (requiere setup adicional)
pip install git+https://github.com/trevorhobenshield/twitter-api-client

# Script de descarga
python3 scripts/download_space.py "SPACE_URL" -e 075 -m twitter-api
```

---

## Troubleshooting

### No recibo el correo de TwitterSpaceGPT

**Soluciones:**
1. Revisar carpeta de spam
2. Esperar 20-30 minutos (Spaces largos tardan más)
3. Intentar con otro Space para verificar que funciona
4. Usar método alternativo (download como host)

### El MP3 descargado está corrupto

**Soluciones:**
1. Volver a descargar del link
2. Verificar el tamaño del archivo (debe ser proporcional a la duración)
3. Probar abrir con VLC u otro reproductor

### El archivo es muy grande (>25MB)

Para usar Whisper API, comprimir primero:

```bash
# Comprimir a 128kbps (buena calidad, menor tamaño)
ffmpeg -i audio_original.mp3 -b:a 128k audio_comprimido.mp3

# Luego transcribir
python3 scripts/transcribe_audio.py audio_comprimido.mp3
```

---

## Checklist por Episodio

- [ ] Space grabado y completado
- [ ] URL del Space copiada
- [ ] Audio descargado via TwitterSpaceGPT
- [ ] Audio movido a carpeta `raw/`
- [ ] Transcripción generada
- [ ] Transcripción revisada y corregida
- [ ] Contenido generado (hilo, artículo, etc.)
- [ ] Contenido revisado y editado
- [ ] Contenido publicado
- [ ] Archivos organizados y respaldados

---

## Optimizaciones

### Descargar Múltiples Spaces

Si tienes varios Spaces pendientes:

```bash
# 1. Enviar todos los links a TwitterSpaceGPT en lote
# 2. Mientras esperas los correos, preparar carpetas

for ep in 073 074 075; do
    mkdir -p "../E${ep}_2024-12-0X"/{raw,transcripts,content,media}
done

# 3. Cuando lleguen los correos, descargar y procesar
```

### Automatizar con Cron (Avanzado)

Para procesar automáticamente después de tus Spaces:

```bash
# Agregar a crontab (ejecutar cada martes y jueves a las 2 PM)
0 14 * * 2,4 /path/to/check_and_process_spaces.sh
```

---

**Última actualización:** Diciembre 2024
**Método recomendado:** TwitterSpaceGPT (https://www.twitterspacegpt.com/downloaders)

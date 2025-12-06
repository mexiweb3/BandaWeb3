# BandaWeb3 Automation - Quick Reference

## 🚀 Comandos Principales

### Método 1: Automatización Completa (Todo en Uno)

```bash
# Descarga automática + procesamiento completo
python3 scripts/auto_download_agent.py "SPACE_URL" -e 075 --process

# Ejemplo:
python3 scripts/auto_download_agent.py "https://twitter.com/i/spaces/1ABC..." -e 075 --process
```

**Esto hace:**
1. ⏳ Envía Space a TwitterSpaceGPT (paso manual)
2. 📧 Monitorea tu email esperando link de descarga
3. ⬇️ Descarga MP3 automáticamente
4. 📝 Transcribe con Whisper API
5. ✨ Genera todo el contenido con Claude API

**Tiempo total:** ~15-20 minutos (incluyendo espera de email)

---

### Método 2: Solo Procesamiento (Ya tienes el MP3)

```bash
# Procesar episodio existente
./scripts/process_episode.sh 075 ~/Downloads/space_audio.mp3

# Con opciones
./scripts/process_episode.sh 075 ~/Downloads/space.mp3 --date 2024-12-03
./scripts/process_episode.sh 075 ~/Downloads/space.mp3 --only-thread
./scripts/process_episode.sh 075 ~/Downloads/space.mp3 --skip-transcription
```

**Tiempo:** ~8-10 minutos

---

### Método 3: Paso por Paso

#### 1. Descargar Audio Manualmente
```
https://www.twitterspacegpt.com/downloaders
→ Pegar URL del Space
→ Esperar correo
→ Descargar MP3
```

#### 2. Transcribir
```bash
python3 scripts/transcribe_audio.py ~/Downloads/space.mp3
```

#### 3. Generar Contenido
```bash
# Todo el contenido
python3 scripts/generate_content.py ../E075_2024-12-05

# Solo hilo de X
python3 scripts/generate_content.py ../E075_2024-12-05 -t thread

# Solo artículo
python3 scripts/generate_content.py ../E075_2024-12-05 -t article

# Solo highlights
python3 scripts/generate_content.py ../E075_2024-12-05 -t highlights
```

---

## 📁 Estructura de Salida

Después de procesar, cada episodio tiene:

```
E075_2024-12-05/
├── raw/
│   └── audio.mp3                    # Audio original
├── transcripts/
│   ├── transcription.txt            # Texto plano
│   ├── transcription.json           # Con timestamps
│   └── transcription.srt            # Subtítulos
├── content/
│   ├── thread_x.json                # Hilo para X (listo para publicar)
│   ├── article.md                   # Artículo largo
│   ├── post_linkedin.txt            # Post LinkedIn
│   └── video_highlights.json        # Momentos para clips
└── metadata.json                    # Info del episodio
```

---

## 🔍 Ver Resultados

```bash
# Variable con carpeta del episodio
EPISODE_DIR="../E075_2024-12-05"

# Ver transcripción
cat "$EPISODE_DIR/transcripts/transcription.txt"

# Ver hilo de X
cat "$EPISODE_DIR/content/thread_x.json"

# Ver artículo
cat "$EPISODE_DIR/content/article.md"

# Ver highlights
cat "$EPISODE_DIR/content/video_highlights.json"

# Ver metadata
cat "$EPISODE_DIR/metadata.json"
```

---

## ⚙️ Configuración Inicial

### Primera Vez (Solo una vez)

```bash
cd bandaweb3-automation

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar credenciales
cp config/.env.example config/.env
nano config/.env

# Agregar:
# - OPENAI_API_KEY (para Whisper)
# - ANTHROPIC_API_KEY (para Claude)
# - DOWNLOAD_EMAIL (tu email)
# - DOWNLOAD_EMAIL_PASSWORD (App Password de Gmail)
```

### Crear App Password de Gmail

1. Ir a: https://myaccount.google.com/apppasswords
2. Crear nueva contraseña para "BandaWeb3 Automation"
3. Copiar la contraseña generada
4. Pegarla en `DOWNLOAD_EMAIL_PASSWORD` en `.env`

---

## 🎯 Workflows Típicos

### Workflow Post-Space (Martes/Jueves)

```bash
# 1. Inmediatamente después del Space
python3 scripts/auto_download_agent.py "SPACE_URL" -e 075 --process

# 2. Mientras procesa (15-20 min), tomar café ☕

# 3. Revisar contenido generado
cat ../E075_*/content/thread_x.json

# 4. Publicar en X
# (Copiar JSON y publicar manualmente o con tu herramienta)
```

### Workflow Batch (Varios episodios)

```bash
# Procesar episodios viejos
./scripts/process_episode.sh 073 "../073/audio.mp3" --date 2024-12-03
./scripts/process_episode.sh 074 "../074/audio.mp3" --date 2024-12-04
./scripts/process_episode.sh 075 "../075/audio.mp3"
```

### Workflow Rápido (Solo Hilo)

```bash
# Solo generar hilo de X
python3 scripts/transcribe_audio.py ~/Downloads/space.mp3
python3 scripts/generate_content.py ../E075_* -t thread

# Tiempo: ~5-7 minutos
```

---

## 🐛 Troubleshooting Rápido

### Email no llega de TwitterSpaceGPT
```bash
# Revisar spam
# Esperar 20-30 minutos para Spaces largos
# Verificar que enviaste URL correcta
```

### Error: API Key not found
```bash
# Verificar .env
cat config/.env | grep OPENAI_API_KEY

# Si está vacío, agregar
echo "OPENAI_API_KEY=sk-..." >> config/.env
```

### Archivo muy grande (>25MB)
```bash
# Comprimir con ffmpeg
ffmpeg -i audio_grande.mp3 -b:a 128k audio_comprimido.mp3

# Luego transcribir
python3 scripts/transcribe_audio.py audio_comprimido.mp3
```

### Re-generar solo un tipo de contenido
```bash
# Ya tienes transcripción, pero quieres regenerar solo el hilo
python3 scripts/generate_content.py ../E075_* -t thread
```

---

## 💰 Costos por Episodio

| Servicio | Costo | Por Qué |
|----------|-------|---------|
| TwitterSpaceGPT | $0 | Gratis |
| Whisper API | ~$5.40 | 90 min de audio @ $0.006/min |
| Claude API | ~$3-5 | Generación de contenido |
| **Total** | **~$8-10** | Por episodio completo |

**Mensual (8 episodios):** ~$64-80

---

## 📞 Referencias Rápidas

- **Setup completo:** [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Ejemplos detallados:** [EJEMPLOS.md](EJEMPLOS.md)
- **Descarga de audio:** [docs/DOWNLOAD_AUDIO.md](docs/DOWNLOAD_AUDIO.md)
- **Auto-download agent:** [docs/AUTO_DOWNLOAD_AGENT.md](docs/AUTO_DOWNLOAD_AGENT.md)

---

**Última actualización:** Diciembre 2024

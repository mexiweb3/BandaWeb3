# BandaWeb3 Automation - Guía de Inicio Rápido

## 🚀 Setup Inicial (15 minutos)

### 1. Prerequisitos

```bash
# Verificar instalaciones
python3 --version  # Debe ser 3.11+
pip --version
ffmpeg -version
```

Si falta algo:
```bash
# Instalar Python dependencies
pip install -r requirements.txt

# Si necesitas ffmpeg (ya lo tienes instalado)
# En Linux: sudo apt install ffmpeg
# En Mac: brew install ffmpeg
```

### 2. Configurar API Keys

```bash
# Copiar template de environment
cd bandaweb3-automation/config
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o usa tu editor favorito
```

**API Keys necesarias:**

1. **OpenAI** (para Whisper - transcripción)
   - Ir a: https://platform.openai.com/api-keys
   - Crear nueva key
   - Copiar en `OPENAI_API_KEY`
   - Costo estimado: ~$0.006/minuto de audio ($3.60 por hora)

2. **Anthropic** (para Claude - generación de contenido)
   - Ir a: https://console.anthropic.com/
   - Crear nueva key
   - Copiar en `ANTHROPIC_API_KEY`
   - Costo estimado: ~$15-30/episodio

3. **X API Pro** (ya lo tienes)
   - Ir a: https://developer.twitter.com/en/portal/dashboard
   - Copiar tus credenciales existentes

### 3. Probar Instalación

```bash
cd bandaweb3-automation

# Test 1: Verificar environment
python3 -c "from dotenv import load_dotenv; import os; load_dotenv('config/.env'); print('✓ Env loaded')"

# Test 2: Verificar OpenAI
python3 -c "import openai; print('✓ OpenAI installed')"

# Test 3: Verificar Anthropic
python3 -c "import anthropic; print('✓ Anthropic installed')"
```

---

## 📝 Uso Básico - Procesar un Space

### Opción A: Proceso Manual (Recomendado al inicio)

#### Paso 1: Descargar Audio del Space

**Como host del Space:**
1. Ve a X (Twitter)
2. Abre tu Space completado
3. Descarga el archivo (disponible 30 días)
4. Guárdalo en la carpeta del episodio

```bash
# Crear estructura de carpetas
mkdir -p "../E075_2024-12-05/raw"
mkdir -p "../E075_2024-12-05/transcripts"
mkdir -p "../E075_2024-12-05/content"

# Mover tu archivo descargado
mv ~/Downloads/space_audio.mp3 "../E075_2024-12-05/raw/audio.mp3"
```

#### Paso 2: Transcribir Audio

```bash
python3 scripts/transcribe_audio.py "../E075_2024-12-05/raw/audio.mp3"
```

**Salida esperada:**
- `../E075_2024-12-05/transcripts/transcription.txt` - Texto plano
- `../E075_2024-12-05/transcripts/transcription.json` - Con timestamps
- `../E075_2024-12-05/transcripts/transcription.srt` - Formato subtítulos

**Tiempo estimado:** 2-5 minutos (depende de duración del audio)

#### Paso 3: Generar Contenido

```bash
python3 scripts/generate_content.py "../E075_2024-12-05"
```

**Salida esperada:**
- `../E075_2024-12-05/content/thread_x.json` - Hilo para X
- `../E075_2024-12-05/content/article.md` - Artículo largo
- `../E075_2024-12-05/content/post_linkedin.txt` - Post LinkedIn
- `../E075_2024-12-05/content/video_highlights.json` - Momentos destacados

**Tiempo estimado:** 3-5 minutos

### Opción B: Proceso Automático (Próximamente)

```bash
# Usando el script automatizado (cuando esté listo)
python3 scripts/download_space.py "https://twitter.com/i/spaces/SPACE_ID" -e 075

# Esto ejecutará automáticamente:
# 1. Descarga de audio
# 2. Transcripción
# 3. Generación de contenido
```

---

## 🎯 Workflows Típicos

### Workflow 1: Post-Space Rápido

**Tiempo total: ~10 minutos**

```bash
# 1. Descargar audio manualmente a carpeta
# 2. Transcribir
python3 scripts/transcribe_audio.py "../E075_2024-12-05/raw/audio.mp3"

# 3. Generar solo hilo de X (más rápido)
python3 scripts/generate_content.py "../E075_2024-12-05" -t thread

# 4. Revisar y publicar
cat "../E075_2024-12-05/content/thread_x.json"
```

### Workflow 2: Contenido Completo

**Tiempo total: ~15 minutos**

```bash
# 1. Descargar audio
# 2. Transcribir
python3 scripts/transcribe_audio.py "../E075_2024-12-05/raw/audio.mp3"

# 3. Generar TODO el contenido
python3 scripts/generate_content.py "../E075_2024-12-05" -t all

# 4. Revisar archivos generados
ls -lh "../E075_2024-12-05/content/"
```

### Workflow 3: Solo Highlights (para clips)

```bash
# Generar solo momentos destacados
python3 scripts/generate_content.py "../E075_2024-12-05" -t highlights

# Ver highlights identificados
cat "../E075_2024-12-05/content/video_highlights.json"
```

---

## 📊 Estructura de Archivos Resultante

```
E075_2024-12-05/
├── raw/
│   └── audio.mp3                    # Audio original
├── transcripts/
│   ├── transcription.txt            # Texto plano
│   ├── transcription.json           # Con timestamps
│   └── transcription.srt            # Subtítulos
├── content/
│   ├── thread_x.json                # Hilo para X
│   ├── article.md                   # Artículo largo
│   ├── post_linkedin.txt            # Post LinkedIn
│   └── video_highlights.json        # Momentos clave
└── metadata.json                    # Metadata del episodio
```

---

## ⚡ Tips y Mejores Prácticas

### Optimizar Costos

1. **Whisper API:**
   - Comprimir audio antes de enviar (reduce costos)
   - Usar formato MP3 a 128kbps es suficiente

2. **Claude API:**
   - Generar solo lo que necesites (`-t thread` vs `-t all`)
   - Revisar transcripciones primero para evitar re-generaciones

### Mejorar Calidad

1. **Transcripciones:**
   - Audio limpio = mejor transcripción
   - Revisar nombres de invitados y corregir en JSON

2. **Contenido Generado:**
   - Editar prompts en `scripts/generate_content.py` según tu estilo
   - Experimentar con diferentes enfoques

### Workflow Eficiente

1. **Durante el Space:**
   - Activa grabación
   - Toma notas de momentos destacados

2. **Post-Space inmediato:**
   - Descarga audio mientras esté fresco
   - Genera transcripción

3. **Review tranquilo:**
   - Revisa transcripción
   - Genera contenido
   - Edita y publica

---

## 🚨 Troubleshooting

### Error: "OPENAI_API_KEY not found"
```bash
# Verificar que .env existe y tiene la key
cat config/.env | grep OPENAI_API_KEY

# Si no existe, agregar:
echo "OPENAI_API_KEY=tu-key-aqui" >> config/.env
```

### Error: "File size exceeds 25 MB limit"
```bash
# Comprimir audio con ffmpeg
ffmpeg -i audio_grande.mp3 -b:a 128k audio_comprimido.mp3
```

### Transcripción en idioma incorrecto
```bash
# Forzar español
python3 scripts/transcribe_audio.py audio.mp3 -l es
```

---

## 📞 Próximos Pasos

1. ✅ Procesar tus 2 episodios existentes (#073 y #074)
2. ⏭️ Configurar n8n para automatización completa
3. ⏭️ Crear flujo de generación de video clips
4. ⏭️ Integrar publicación automática en redes

---

**¿Preguntas?** Consulta la documentación completa en `docs/`

**¿Encontraste un bug?** Anótalo para mejoras futuras

**¿Funcionó bien?** ¡Empieza a procesar tus Spaces! 🚀

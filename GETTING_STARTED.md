# BandaWeb3 Automation - Getting Started

## 🎯 Lo Que Este Sistema Hace

Este sistema automatiza **completamente** el proceso de convertir tus Twitter Spaces en contenido listo para publicar:

**Input:** URL de un Twitter Space
**Output (15-20 minutos después):**
- ✅ Transcripción completa con timestamps
- ✅ Hilo de X listo para publicar (10 tweets)
- ✅ Artículo largo en Markdown (1000-1500 palabras)
- ✅ Post para LinkedIn
- ✅ Highlights para video clips (3-4 momentos clave)

---

## 🚀 Setup Inicial (Solo Primera Vez)

### Paso 1: Verificar Prerequisitos

```bash
# Verificar Python
python3 --version  # Debe ser 3.11+

# Verificar pip
pip3 --version

# Verificar ffmpeg (ya instalado)
ffmpeg -version
```

### Paso 2: Instalar Dependencias

```bash
cd /home/davidiego2/Documents/BandaWeb3/074\ Devconnect\ Parte\ 2/bandaweb3-automation

# Instalar paquetes Python
pip3 install -r requirements.txt --user
```

### Paso 3: Configurar API Keys

```bash
# Copiar template
cp config/.env.example config/.env

# Editar con tus credenciales
nano config/.env
```

**API Keys que necesitas:**

#### 1. OpenAI API (Whisper)
- Ir a: https://platform.openai.com/api-keys
- Click "Create new secret key"
- Copiar y pegar en `OPENAI_API_KEY`
- **Costo:** ~$5-6 por episodio de 90 minutos

#### 2. Anthropic API (Claude)
- Ir a: https://console.anthropic.com/
- Settings → API Keys → Create Key
- Copiar y pegar en `ANTHROPIC_API_KEY`
- **Costo:** ~$3-5 por episodio

#### 3. Email Configuration (Gmail)
- Usar tu email actual
- Crear App Password:
  1. Ir a: https://myaccount.google.com/apppasswords
  2. Crear nueva contraseña para "BandaWeb3"
  3. Copiar en `DOWNLOAD_EMAIL_PASSWORD`

**Tu .env debe quedar así:**
```bash
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Email
DOWNLOAD_EMAIL=tu-email@gmail.com
DOWNLOAD_EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

### Paso 4: Verificar Instalación

```bash
# Test básico
python3 -c "import openai, anthropic; print('✅ Todo instalado correctamente')"
```

---

## 🎬 Tu Primer Episodio

### Opción A: Automatización Completa (Recomendado)

```bash
# Un solo comando hace todo
python3 scripts/auto_download_agent.py "https://twitter.com/i/spaces/1ABC..." -e 075 --process
```

**Qué pasa:**
1. Te pide enviar el Space a TwitterSpaceGPT manualmente (por ahora)
2. Monitorea tu email esperando el link de descarga
3. Descarga el MP3 automáticamente
4. Transcribe con Whisper API
5. Genera todo el contenido con Claude
6. Guarda todo organizado en carpetas

**Tiempo total:** 15-20 minutos

### Opción B: Proceso Manual (Más Control)

#### 1. Descargar Audio (5-15 min)
```
1. Ir a: https://www.twitterspacegpt.com/downloaders
2. Pegar URL del Space
3. Ingresar tu email
4. Esperar correo (5-15 min)
5. Descargar MP3
```

#### 2. Procesar Todo (8-10 min)
```bash
# Un comando procesa todo
./scripts/process_episode.sh 075 ~/Downloads/space_audio.mp3
```

#### 3. Revisar Resultados
```bash
# Ver hilo generado
cat ../E075_2024-12-05/content/thread_x.json

# Ver artículo
cat ../E075_2024-12-05/content/article.md

# Ver highlights
cat ../E075_2024-12-05/content/video_highlights.json
```

---

## 📁 Qué Genera el Sistema

Después de procesar, tendrás esta estructura:

```
../E075_2024-12-05/
├── raw/
│   └── audio.mp3                    # Audio original del Space
│
├── transcripts/
│   ├── transcription.txt            # Texto plano completo
│   ├── transcription.json           # Con timestamps por palabra
│   └── transcription.srt            # Formato subtítulos
│
├── content/
│   ├── thread_x.json                # 🎯 Hilo de X (10 tweets)
│   ├── article.md                   # 📝 Artículo largo
│   ├── post_linkedin.txt            # 💼 Post LinkedIn
│   └── video_highlights.json        # 🎬 Momentos para clips
│
└── metadata.json                    # Info del episodio
```

### Ejemplo: thread_x.json

```json
{
  "thread": [
    {
      "order": 1,
      "content": "🔥 Acabamos de cerrar un Space ÉPICO sobre EVVM en ETHGlobal Argentina\n\nAquí los insights más importantes 🧵👇",
      "hashtags": ["EVVM", "ETHGlobal"],
      "characters": 127
    },
    {
      "order": 2,
      "content": "1/10: ¿Qué es EVVM? Es una máquina virtual que permite...",
      "characters": 245
    }
    // ... 8 tweets más
  ]
}
```

---

## 🔄 Workflow Semanal Recomendado

### Martes (Space Regular)

```bash
# 1. Durante el Space: Tomar notas mentales de momentos clave

# 2. Inmediatamente después (2 min):
python3 scripts/auto_download_agent.py "SPACE_URL" -e 075 --process

# 3. Mientras procesa (15-20 min): Responder DMs, revisar menciones

# 4. Revisar contenido (5-10 min):
cat ../E075_*/content/thread_x.json
cat ../E075_*/content/article.md

# 5. Publicar hilo en X (5 min):
# Copiar tweets del JSON y publicar

# 6. Programar artículo para fin de semana
```

**Tiempo total activo:** ~12-17 minutos (vs. 2-3 horas manualmente)

### Jueves (Space Expedito)

```bash
# Mismo proceso
python3 scripts/auto_download_agent.py "SPACE_URL" -e 076 --process
```

---

## 💡 Tips y Trucos

### Ahorrar Tiempo

1. **Procesar en paralelo:**
```bash
# Terminal 1
./scripts/process_episode.sh 073 audio073.mp3

# Terminal 2 (simultáneo)
./scripts/process_episode.sh 074 audio074.mp3
```

2. **Solo lo que necesites:**
```bash
# Solo hilo (más rápido)
python3 scripts/generate_content.py ../E075_* -t thread

# Solo highlights
python3 scripts/generate_content.py ../E075_* -t highlights
```

### Ahorrar Dinero

1. **Comprimir audio antes:**
```bash
ffmpeg -i audio_original.mp3 -b:a 96k audio_comprimido.mp3
# 96kbps es suficiente para voz, reduce costos
```

2. **Generar selectivamente:**
- No regeneres todo si solo necesitas ajustar el hilo
- Edita manualmente en vez de hacer nueva llamada a API

### Mejorar Calidad

1. **Revisar transcripciones:**
- Corregir nombres propios en el JSON
- Verificar términos técnicos

2. **Personalizar prompts:**
- Editar `scripts/generate_content.py`
- Ajustar PROMPTS según tu estilo

---

## 🆘 Problemas Comunes

### "No recibo email de TwitterSpaceGPT"
- ✅ Revisar carpeta spam
- ✅ Esperar 20-30 min (Spaces largos tardan más)
- ✅ Verificar que URL del Space sea correcta

### "Error: OPENAI_API_KEY not found"
```bash
# Verificar .env
cat config/.env | grep OPENAI_API_KEY

# Si está vacío
nano config/.env
# Agregar: OPENAI_API_KEY=sk-...
```

### "File size exceeds 25 MB limit"
```bash
# Comprimir audio
ffmpeg -i grande.mp3 -b:a 128k comprimido.mp3

# Luego procesar
python3 scripts/transcribe_audio.py comprimido.mp3
```

### "Transcripción en idioma incorrecto"
```bash
# Forzar español
python3 scripts/transcribe_audio.py audio.mp3 -l es
```

---

## 📊 Costos Reales

### Por Episodio (90 minutos)
- TwitterSpaceGPT: **$0** (gratis)
- Whisper API: **~$5.40** (transcripción)
- Claude API: **~$3-5** (contenido)
- **Total: ~$8-10 por episodio**

### Mensual (8 episodios)
- **~$64-80/mes**
- Comparado con: Contratar editor ($500+/mes) o hacerlo manual (20+ horas/mes)

---

## 📚 Documentación Completa

- 📖 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Comandos y referencia rápida
- 📘 [EJEMPLOS.md](EJEMPLOS.md) - 8 casos de uso detallados
- 📕 [docs/QUICKSTART.md](docs/QUICKSTART.md) - Guía completa de setup
- 📗 [docs/DOWNLOAD_AUDIO.md](docs/DOWNLOAD_AUDIO.md) - Métodos de descarga
- 📙 [docs/AUTO_DOWNLOAD_AGENT.md](docs/AUTO_DOWNLOAD_AGENT.md) - Agente de descarga

---

## ✅ Próximos Pasos

1. [ ] Completar setup de API keys
2. [ ] Procesar episodios #073 y #074 existentes
3. [ ] Configurar n8n para automatización avanzada (próximamente)
4. [ ] Crear pipeline de video clips (próximamente)

---

## 🎉 ¡Listo!

Ya tienes todo configurado. Tu próximo Space tomará solo **15-20 minutos** de procesamiento automático.

**Comando para usar:**
```bash
python3 scripts/auto_download_agent.py "SPACE_URL" -e <NUMERO> --process
```

**¿Dudas?** Consulta la documentación o experimenta con los scripts.

**¿Funciona bien?** ¡Empieza a procesar tus Spaces! 🚀

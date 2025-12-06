# BandaWeb3 Automation & Archives

Sistema integral para la gestión, descarga y publicación del contenido de BandaWeb3 (Twitter Spaces).

## 🌟 Características

### 🤖 Automatización AI
- **Auto-Download:** Descarga automática de Spaces desde emails.
- **Transcripción:** Uso de Whisper API para texto preciso en español.
- **Generación de Contenido:** Artículos, hilos y posts usando Claude 3.5 Sonnet.
- [Ver documentación del sistema AI](SYSTEM_OVERVIEW.md)

### 🗄️ Archivo Histórico (Co-hosted Spaces)
- **Ingestión Masiva:** Scripts para importar historiales de Spaces.
- **Sitio Web Estático:** Generador de sitio web completo (HTML/CSS) con 300+ episodios.
- **Base de Datos:** JSON estructurado con metadatos y conteo de oyentes.
- [Ver documentación de Co-hosted Spaces](docs/CO_HOSTED_SPACES.md)

## 🚀 Inicio Rápido

### Instalación
```bash
pip install -r requirements.txt
```

### Generar Sitio Web
```bash
python3 scripts/generate_website.py
```
El sitio se generará en `website/output/`.

### Procesar un Space (AI)
```bash
# Requiere .env configurado
python3 scripts/auto_download_agent.py "URL_DEL_SPACE" --process
```

## 📚 Documentación
- [Guía de Inicio](GETTING_STARTED.md)
- [ Estado del Sistema](STATUS.md)
- [Overview Técnico](SYSTEM_OVERVIEW.md)
- [Co-hosted Spaces Workflows](docs/CO_HOSTED_SPACES.md)
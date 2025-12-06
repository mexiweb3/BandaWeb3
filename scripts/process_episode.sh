#!/bin/bash
# BandaWeb3 - Script de Procesamiento Completo de Episodios
# Automatiza: organización, transcripción y generación de contenido

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check arguments
if [ $# -lt 2 ]; then
    echo "Uso: $0 <numero_episodio> <archivo_audio.mp3> [opciones]"
    echo ""
    echo "Ejemplo:"
    echo "  $0 075 ~/Downloads/space_audio.mp3"
    echo ""
    echo "Opciones:"
    echo "  --skip-transcription    Saltar transcripción (si ya existe)"
    echo "  --only-thread          Generar solo hilo de X"
    echo "  --date YYYY-MM-DD      Especificar fecha (default: hoy)"
    exit 1
fi

EPISODE=$1
AUDIO_FILE=$2
SKIP_TRANSCRIPTION=false
CONTENT_TYPE="all"
CUSTOM_DATE=""

# Parse optional arguments
shift 2
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-transcription)
            SKIP_TRANSCRIPTION=true
            shift
            ;;
        --only-thread)
            CONTENT_TYPE="thread"
            shift
            ;;
        --date)
            CUSTOM_DATE="$2"
            shift 2
            ;;
        *)
            print_error "Opción desconocida: $1"
            exit 1
            ;;
    esac
done

# Set date
if [ -n "$CUSTOM_DATE" ]; then
    DATE=$CUSTOM_DATE
else
    DATE=$(date +%Y-%m-%d)
fi

# Set episode directory
BASE_DIR="$(dirname "$0")/.."
EPISODE_DIR="${BASE_DIR}/../E${EPISODE}_${DATE}"

# Validate audio file exists
if [ ! -f "$AUDIO_FILE" ]; then
    print_error "Archivo de audio no encontrado: $AUDIO_FILE"
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║     BandaWeb3 - Procesamiento de Episodio         ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Episodio: #$EPISODE"
echo "Fecha: $DATE"
echo "Audio: $AUDIO_FILE"
echo "Directorio: $EPISODE_DIR"
echo ""

# Step 1: Create directory structure
print_step "Creando estructura de carpetas..."
mkdir -p "$EPISODE_DIR"/{raw,transcripts,content,media}
print_success "Estructura creada"

# Step 2: Copy audio file
print_step "Copiando archivo de audio..."
cp "$AUDIO_FILE" "$EPISODE_DIR/raw/audio.mp3"
AUDIO_SIZE=$(du -h "$EPISODE_DIR/raw/audio.mp3" | cut -f1)
print_success "Audio copiado ($AUDIO_SIZE)"

# Step 3: Create metadata
print_step "Creando metadata..."
cat > "$EPISODE_DIR/metadata.json" <<EOF
{
  "episode_number": "$EPISODE",
  "date": "$DATE",
  "audio_file": "raw/audio.mp3",
  "processed_at": "$(date -Iseconds)",
  "status": "processing"
}
EOF
print_success "Metadata creada"

# Step 4: Transcription
if [ "$SKIP_TRANSCRIPTION" = true ]; then
    print_warning "Saltando transcripción (--skip-transcription)"
else
    print_step "Iniciando transcripción con Whisper API..."
    echo "   Esto puede tomar 2-5 minutos dependiendo de la duración..."

    cd "$BASE_DIR"
    if python3 scripts/transcribe_audio.py "$EPISODE_DIR/raw/audio.mp3" --output "$EPISODE_DIR/transcripts"; then
        print_success "Transcripción completada"
    else
        print_error "Error en transcripción"
        exit 1
    fi
fi

# Verify transcription exists
if [ ! -f "$EPISODE_DIR/transcripts/transcription.txt" ]; then
    print_error "No se encontró transcripción. Use --skip-transcription solo si ya existe."
    exit 1
fi

# Step 5: Content generation
print_step "Generando contenido con Claude API..."
echo "   Esto puede tomar 3-5 minutos..."

cd "$BASE_DIR"
if [ "$CONTENT_TYPE" = "thread" ]; then
    print_warning "Generando solo hilo de X (--only-thread)"
    if python3 scripts/generate_content.py "$EPISODE_DIR" -t thread; then
        print_success "Hilo generado"
    else
        print_error "Error generando hilo"
        exit 1
    fi
else
    if python3 scripts/generate_content.py "$EPISODE_DIR"; then
        print_success "Contenido generado"
    else
        print_error "Error generando contenido"
        exit 1
    fi
fi

# Step 6: Update metadata
print_step "Actualizando metadata..."
python3 -c "
import json
with open('$EPISODE_DIR/metadata.json', 'r+') as f:
    data = json.load(f)
    data['status'] = 'completed'
    data['completed_at'] = '$(date -Iseconds)'
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
"
print_success "Metadata actualizada"

# Final summary
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║              ✅ PROCESAMIENTO COMPLETO             ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "📁 Archivos generados en: $EPISODE_DIR"
echo ""

# List generated files
echo "📄 Transcripciones:"
if [ -f "$EPISODE_DIR/transcripts/transcription.txt" ]; then
    WORDS=$(wc -w < "$EPISODE_DIR/transcripts/transcription.txt")
    echo "   ✓ transcription.txt ($WORDS palabras)"
fi
if [ -f "$EPISODE_DIR/transcripts/transcription.json" ]; then
    echo "   ✓ transcription.json (con timestamps)"
fi
if [ -f "$EPISODE_DIR/transcripts/transcription.srt" ]; then
    echo "   ✓ transcription.srt (subtítulos)"
fi

echo ""
echo "✨ Contenido:"
if [ -f "$EPISODE_DIR/content/thread_x.json" ]; then
    echo "   ✓ thread_x.json (hilo para X)"
fi
if [ -f "$EPISODE_DIR/content/article.md" ]; then
    ARTICLE_WORDS=$(wc -w < "$EPISODE_DIR/content/article.md")
    echo "   ✓ article.md ($ARTICLE_WORDS palabras)"
fi
if [ -f "$EPISODE_DIR/content/post_linkedin.txt" ]; then
    echo "   ✓ post_linkedin.txt"
fi
if [ -f "$EPISODE_DIR/content/video_highlights.json" ]; then
    echo "   ✓ video_highlights.json"
fi

echo ""
echo "📋 Próximos pasos:"
echo "   1. Revisar transcripción:"
echo "      cat \"$EPISODE_DIR/transcripts/transcription.txt\""
echo ""
echo "   2. Ver hilo de X:"
echo "      cat \"$EPISODE_DIR/content/thread_x.json\""
echo ""
echo "   3. Leer artículo:"
echo "      cat \"$EPISODE_DIR/content/article.md\""
echo ""
echo "   4. Ver highlights para videos:"
echo "      cat \"$EPISODE_DIR/content/video_highlights.json\""
echo ""
echo "🚀 ¡Listo para publicar!"
echo ""

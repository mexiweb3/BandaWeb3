#!/bin/bash
# Script para exponer archivo local y probar Fireflies

echo "=========================================="
echo "FIREFLIES TEST - Exposición de archivo"
echo "=========================================="
echo ""

# Configuración
AUDIO_FILE="shared/audio/1kvJpbwePbwKE.mp3"
PORT=9876

# Verificar que el archivo existe
if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ Error: No se encontró $AUDIO_FILE"
    exit 1
fi

echo "📁 Archivo: $AUDIO_FILE"
echo "🌐 Puerto local: $PORT"
echo ""

# Iniciar servidor HTTP en background
echo "🚀 Iniciando servidor HTTP local..."
cd shared/audio
python3 -m http.server $PORT > /dev/null 2>&1 &
HTTP_PID=$!
cd ../..

sleep 2

echo "✅ Servidor HTTP iniciado (PID: $HTTP_PID)"
echo ""

# Usar localhost.run para exponer el servidor
echo "🌍 Creando túnel público con localhost.run..."
echo "   (Esto puede tomar unos segundos)"
echo ""

# Ejecutar SSH tunnel y capturar la URL
ssh -R 80:localhost:$PORT localhost.run > tunnel_output.txt 2>&1 &
TUNNEL_PID=$!

# Esperar a que se establezca el túnel
sleep 5

# Extraer la URL del output
PUBLIC_URL=$(grep -oP 'https://[a-z0-9-]+\.lhr\.life' tunnel_output.txt | head -1)

if [ -z "$PUBLIC_URL" ]; then
    echo "❌ No se pudo crear el túnel público"
    echo "   Salida del túnel:"
    cat tunnel_output.txt
    kill $HTTP_PID $TUNNEL_PID 2>/dev/null
    rm tunnel_output.txt
    exit 1
fi

echo "✅ Túnel creado exitosamente!"
echo ""
echo "📍 URL pública del archivo:"
echo "   $PUBLIC_URL/1kvJpbwePbwKE.mp3"
echo ""
echo "Ahora puedes usar esta URL con Fireflies."
echo ""
echo "Presiona Ctrl+C cuando termines para cerrar el servidor y el túnel."
echo ""

# Mantener el script corriendo
trap "echo ''; echo '🛑 Cerrando servidor y túnel...'; kill $HTTP_PID $TUNNEL_PID 2>/dev/null; rm tunnel_output.txt; echo '✅ Limpieza completada'; exit 0" INT

# Esperar indefinidamente
tail -f /dev/null

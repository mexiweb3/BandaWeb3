#!/usr/bin/env python3
"""
Script para enviar múltiples Twitter Spaces a TwitterSpaceGPT para descarga
usando solicitudes HTTP directas (sin navegador)
"""

import requests
import json
import time
from pathlib import Path

def load_json(filepath):
    """Carga un archivo JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def submit_space_to_download(space_url, email):
    """
    Envía un Space a TwitterSpaceGPT para descarga
    
    Args:
        space_url: URL del Twitter Space
        email: Email donde se enviará el link de descarga
    
    Returns:
        bool: True si fue exitoso, False si falló
    """
    
    # URL del endpoint (puede necesitar ajustes según la API real)
    api_url = "https://www.twitterspacegpt.com/api/download"
    
    # Datos del formulario
    payload = {
        'email': email,
        'space_url': space_url
    }
    
    # Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://www.twitterspacegpt.com',
        'Referer': 'https://www.twitterspacegpt.com/downloaders'
    }
    
    try:
        print(f"📤 Enviando: {space_url}")
        
        # Hacer la solicitud POST
        response = requests.post(api_url, data=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print(f"   ✅ Enviado exitosamente")
            return True
        else:
            print(f"   ⚠️  Status code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def get_latest_hosted_spaces(n=5):
    """
    Obtiene los últimos N spaces hosteados de episodes_database.json
    
    Args:
        n: Número de spaces a obtener
    
    Returns:
        list: Lista de episodios
    """
    
    # Cargar episodes_database
    data = load_json('shared/episodes_database.json')
    
    # Filtrar solo hosted (no co-hosted) y que tengan space_url
    hosted = [ep for ep in data['episodes'] 
              if ep.get('type') != 'co-hosted' and ep.get('space_url')]
    
    # Ordenar por fecha (más reciente primero)
    hosted.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    # Tomar los últimos N
    return hosted[:n]

def main():
    """Función principal"""
    
    print("\n" + "="*100)
    print("ENVIANDO SPACES A TWITTERSPACEGPT PARA DESCARGA")
    print("="*100 + "\n")
    
    # Configuración
    email = "vanillacokedrinker@gmail.com"
    num_spaces = 5
    
    # Obtener los últimos spaces
    print(f"📊 Obteniendo los últimos {num_spaces} spaces hosteados...\n")
    spaces = get_latest_hosted_spaces(num_spaces)
    
    print(f"Encontrados {len(spaces)} spaces:\n")
    for i, ep in enumerate(spaces, 1):
        print(f"{i}. {ep.get('title', 'N/A')}")
        print(f"   Fecha: {ep.get('date', 'N/A')} | Duración: {ep.get('duration', 'N/A')}")
        print(f"   URL: {ep.get('space_url', 'N/A')}\n")
    
    print("="*100)
    print("ENVIANDO SOLICITUDES...\n")
    
    # Enviar cada space
    successful = 0
    failed = 0
    
    for i, ep in enumerate(spaces, 1):
        space_url = ep.get('space_url', '')
        
        # Limpiar URL (remover parámetros query)
        if '?' in space_url:
            space_url = space_url.split('?')[0]
        
        print(f"\n[{i}/{len(spaces)}] {ep.get('title', 'N/A')}")
        
        if submit_space_to_download(space_url, email):
            successful += 1
        else:
            failed += 1
        
        # Esperar un poco entre solicitudes para no saturar el servidor
        if i < len(spaces):
            print("   ⏳ Esperando 2 segundos...")
            time.sleep(2)
    
    # Resumen
    print("\n" + "="*100)
    print("RESUMEN")
    print("="*100)
    print(f"✅ Exitosos: {successful}")
    print(f"❌ Fallidos: {failed}")
    print(f"📧 Los links de descarga se enviarán a: {email}")
    print("="*100 + "\n")
    
    print("💡 Nota: Si las solicitudes fallaron, es posible que el endpoint de la API")
    print("   sea diferente. Puedes intentar enviarlos manualmente o inspeccionar")
    print("   las solicitudes de red en el navegador para encontrar el endpoint correcto.\n")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Script para monitorear Gmail usando Gmail API y descargar MP3s de TwitterSpaceGPT
"""

import os
import re
import time
import base64
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

# Scopes necesarios para leer Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Autentica con Gmail API"""
    creds = None
    
    # El archivo token.json almacena los tokens de acceso del usuario
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay credenciales válidas, solicitar login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guardar credenciales para la próxima ejecución
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_gmail_service():
    """Crea y retorna el servicio de Gmail API"""
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    return service

def extract_mp3_links(text):
    """Extrae links de MP3 del texto"""
    pattern = r'https://[^\s<>"]+\.mp3'
    links = re.findall(pattern, text)
    return links

def get_message_body(service, msg_id):
    """Obtiene el cuerpo del mensaje"""
    try:
        message = service.users().messages().get(
            userId='me', 
            id=msg_id, 
            format='full'
        ).execute()
        
        payload = message['payload']
        body_text = ""
        
        # Extraer el cuerpo del mensaje
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' or part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        body_text += base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
        elif 'body' in payload and 'data' in payload['body']:
            body_text = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')
        
        return body_text
    except Exception as e:
        print(f"   ❌ Error al obtener mensaje: {e}")
        return ""

def check_for_new_emails(service, sender_filter="twitterspacegpt"):
    """Busca emails nuevos de TwitterSpaceGPT"""
    try:
        # Buscar mensajes no leídos del remitente
        query = f'from:{sender_filter} is:unread'
        
        results = service.users().messages().list(
            userId='me',
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("📭 No hay emails nuevos")
            return []
        
        print(f"📬 Encontrados {len(messages)} emails nuevos")
        
        mp3_links = []
        
        for msg in messages:
            msg_id = msg['id']
            
            # Obtener detalles del mensaje
            message = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='metadata',
                metadataHeaders=['Subject', 'From']
            ).execute()
            
            # Obtener subject
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            
            print(f"\n📨 Email: {subject}")
            
            # Obtener cuerpo del mensaje
            body = get_message_body(service, msg_id)
            
            # Extraer links de MP3
            links = extract_mp3_links(body)
            
            if links:
                print(f"   ✅ Encontrados {len(links)} links de MP3:")
                for link in links:
                    print(f"      - {link}")
                    mp3_links.append(link)
                
                # Marcar como leído (DESACTIVADO)
                # service.users().messages().modify(
                #    userId='me',
                #    id=msg_id,
                #    body={'removeLabelIds': ['UNREAD']}
                # ).execute()
        
        return mp3_links
        
    except Exception as e:
        print(f"❌ Error al revisar emails: {e}")
        return []

def download_mp3(url, output_dir="shared/audio"):
    """Descarga un archivo MP3"""
    try:
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Extraer nombre del archivo
        filename = url.split("/")[-1]
        output_path = os.path.join(output_dir, filename)
        
        # Verificar si ya existe
        if os.path.exists(output_path):
            print(f"   ⏭️  Ya existe: {filename}")
            return output_path
        
        print(f"   📥 Descargando: {filename}")
        
        # Descargar
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"   📊 Progreso: {percent:.1f}%", end='\r')
        
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n   ✅ Descargado: {output_path} ({file_size_mb:.2f} MB)")
        return output_path
        
    except Exception as e:
        print(f"   ❌ Error al descargar: {e}")
        return None

def monitor_and_download(check_interval=60, max_checks=60):
    """
    Monitorea Gmail y descarga automáticamente los MP3
    
    Args:
        check_interval: Segundos entre cada revisión (default: 60)
        max_checks: Número máximo de revisiones (default: 60 = 1 hora)
    """
    
    print("\n" + "="*100)
    print("MONITOR DE GMAIL PARA DESCARGAS DE TWITTERSPACEGPT")
    print("="*100 + "\n")
    
    # Autenticar con Gmail
    print("🔐 Autenticando con Gmail API...")
    service = get_gmail_service()
    print("✅ Autenticación exitosa!\n")
    
    print(f"⏰ Monitoreando cada {check_interval} segundos...")
    print(f"🔄 Máximo {max_checks} revisiones ({max_checks * check_interval / 60:.1f} minutos)\n")
    
    all_downloaded = []
    
    for check_num in range(max_checks):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Revisión {check_num + 1}/{max_checks}")
        print("-" * 100)
        
        # Buscar emails nuevos
        mp3_links = check_for_new_emails(service)
        
        # Descargar MP3s
        if mp3_links:
            print(f"\n📥 Descargando {len(mp3_links)} archivos...")
            for link in mp3_links:
                downloaded_path = download_mp3(link)
                if downloaded_path and downloaded_path not in all_downloaded:
                    all_downloaded.append(downloaded_path)
        
        # Esperar antes de la siguiente revisión
        if check_num < max_checks - 1:
            print(f"\n⏳ Esperando {check_interval} segundos hasta la próxima revisión...")
            time.sleep(check_interval)
    
    # Resumen
    print("\n" + "="*100)
    print("RESUMEN")
    print("="*100)
    print(f"✅ Archivos descargados: {len(all_downloaded)}")
    for path in all_downloaded:
        file_size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"   - {path} ({file_size_mb:.2f} MB)")
    print("="*100 + "\n")

def check_once():
    """Revisa Gmail una sola vez y descarga los MP3 encontrados"""
    
    print("\n" + "="*100)
    print("REVISIÓN ÚNICA DE GMAIL")
    print("="*100 + "\n")
    
    # Autenticar
    print("🔐 Autenticando con Gmail API...")
    service = get_gmail_service()
    print("✅ Autenticación exitosa!\n")
    
    # Buscar emails
    mp3_links = check_for_new_emails(service)
    
    # Descargar
    if mp3_links:
        print(f"\n📥 Descargando {len(mp3_links)} archivos...\n")
        for link in mp3_links:
            download_mp3(link)
    else:
        print("\n📭 No se encontraron links de MP3 en emails nuevos")
    
    print("\n" + "="*100 + "\n")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Revisar una sola vez
        check_once()
    elif len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Monitorear continuamente
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        max_checks = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        monitor_and_download(check_interval=interval, max_checks=max_checks)
    else:
        print("\nUso:")
        print("  python3 gmail_monitor.py --once              # Revisar una sola vez")
        print("  python3 gmail_monitor.py --monitor [seg] [n] # Monitorear cada [seg] segundos, [n] veces")
        print("\nEjemplos:")
        print("  python3 gmail_monitor.py --once")
        print("  python3 gmail_monitor.py --monitor 60 30     # Revisar cada 60 seg, 30 veces (30 min)")

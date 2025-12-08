#!/usr/bin/env python3
"""
Script para monitorear Gmail vía IMAP y extraer links de descarga de TwitterSpaceGPT
"""

import imaplib
import email
from email.header import decode_header
import re
import time
from datetime import datetime
import os

# Configuración
GMAIL_USER = "vanillacokedrinker@gmail.com"
GMAIL_APP_PASSWORD = "YOUR_APP_PASSWORD_HERE"  # Reemplazar con la contraseña de aplicación
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def connect_to_gmail():
    """Conecta a Gmail vía IMAP"""
    try:
        print(f"📧 Conectando a {GMAIL_USER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        print("✅ Conexión exitosa!")
        return mail
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return None

def extract_mp3_links(email_body):
    """Extrae links de MP3 del cuerpo del email"""
    # Patrón para links de MP3 de TwitterSpaceGPT
    pattern = r'https://[^\s<>"]+\.mp3'
    links = re.findall(pattern, email_body)
    return links

def check_for_new_emails(mail, sender_filter="twitterspacegpt"):
    """Busca emails nuevos de TwitterSpaceGPT"""
    try:
        # Seleccionar inbox
        mail.select("INBOX")
        
        # Buscar emails del remitente en las últimas 24 horas
        search_criteria = f'(FROM "{sender_filter}" UNSEEN)'
        status, messages = mail.search(None, search_criteria)
        
        if status != "OK":
            print("❌ Error al buscar emails")
            return []
        
        email_ids = messages[0].split()
        
        if not email_ids:
            print("📭 No hay emails nuevos")
            return []
        
        print(f"📬 Encontrados {len(email_ids)} emails nuevos")
        
        mp3_links = []
        
        for email_id in email_ids:
            # Obtener el email
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            
            if status != "OK":
                continue
            
            # Parsear el email
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Obtener subject
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                    
                    print(f"\n📨 Email: {subject}")
                    
                    # Extraer cuerpo del email
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                            elif part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode()
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    # Extraer links de MP3
                    links = extract_mp3_links(body)
                    
                    if links:
                        print(f"   ✅ Encontrados {len(links)} links de MP3:")
                        for link in links:
                            print(f"      - {link}")
                            mp3_links.append(link)
        
        return mp3_links
        
    except Exception as e:
        print(f"❌ Error al revisar emails: {e}")
        return []

def download_mp3(url, output_dir="shared/audio"):
    """Descarga un archivo MP3"""
    try:
        import requests
        
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
                    # Mostrar progreso
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"   📊 Progreso: {percent:.1f}%", end='\r')
        
        print(f"\n   ✅ Descargado: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"   ❌ Error al descargar: {e}")
        return None

def monitor_and_download(check_interval=60, max_checks=30):
    """
    Monitorea el correo y descarga automáticamente los MP3
    
    Args:
        check_interval: Segundos entre cada revisión
        max_checks: Número máximo de revisiones antes de terminar
    """
    
    print("\n" + "="*100)
    print("MONITOR DE CORREO PARA DESCARGAS DE TWITTERSPACEGPT")
    print("="*100 + "\n")
    
    # Conectar a Gmail
    mail = connect_to_gmail()
    
    if not mail:
        print("❌ No se pudo conectar a Gmail. Verifica las credenciales.")
        return
    
    print(f"\n⏰ Monitoreando cada {check_interval} segundos...")
    print(f"🔄 Máximo {max_checks} revisiones ({max_checks * check_interval / 60:.1f} minutos)\n")
    
    all_downloaded = []
    
    for check_num in range(max_checks):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Revisión {check_num + 1}/{max_checks}")
        print("-" * 100)
        
        # Buscar emails nuevos
        mp3_links = check_for_new_emails(mail)
        
        # Descargar MP3s
        if mp3_links:
            print(f"\n📥 Descargando {len(mp3_links)} archivos...")
            for link in mp3_links:
                downloaded_path = download_mp3(link)
                if downloaded_path:
                    all_downloaded.append(downloaded_path)
        
        # Esperar antes de la siguiente revisión
        if check_num < max_checks - 1:
            print(f"\n⏳ Esperando {check_interval} segundos hasta la próxima revisión...")
            time.sleep(check_interval)
    
    # Cerrar conexión
    mail.logout()
    
    # Resumen
    print("\n" + "="*100)
    print("RESUMEN")
    print("="*100)
    print(f"✅ Archivos descargados: {len(all_downloaded)}")
    for path in all_downloaded:
        print(f"   - {path}")
    print("="*100 + "\n")

def check_once():
    """Revisa el correo una sola vez y descarga los MP3 encontrados"""
    
    print("\n" + "="*100)
    print("REVISIÓN ÚNICA DE CORREO")
    print("="*100 + "\n")
    
    # Conectar
    mail = connect_to_gmail()
    
    if not mail:
        return
    
    # Buscar emails
    mp3_links = check_for_new_emails(mail)
    
    # Descargar
    if mp3_links:
        print(f"\n📥 Descargando {len(mp3_links)} archivos...\n")
        for link in mp3_links:
            download_mp3(link)
    else:
        print("\n📭 No se encontraron links de MP3 en emails nuevos")
    
    # Cerrar
    mail.logout()
    
    print("\n" + "="*100 + "\n")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Revisar una sola vez
        check_once()
    else:
        # Monitorear continuamente
        monitor_and_download(check_interval=60, max_checks=30)

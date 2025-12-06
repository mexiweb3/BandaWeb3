#!/usr/bin/env python3
"""
BandaWeb3 - Auto Download Agent
Automatiza descarga de Spaces MP3 desde TwitterSpaceGPT monitoreando email
"""

import os
import sys
import time
import imaplib
import email
import re
import requests
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from email.header import decode_header
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv(dotenv_path="../config/.env")


class SpaceDownloadAgent:
    def __init__(self, email_address, email_password):
        self.email_address = email_address
        self.email_password = email_password
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

    def submit_to_twitterspacegpt(self, space_url, email):
        """
        Submit Space URL to TwitterSpaceGPT

        Note: This is a placeholder - you'll need to inspect the actual form
        submission on their website to get the correct endpoint and parameters
        """
        print(f"📤 Enviando Space a TwitterSpaceGPT...")
        print(f"   URL: {space_url}")
        print(f"   Email: {email}")

        # IMPORTANT: Update this URL and parameters based on actual form
        # You can inspect network requests in browser DevTools
        url = "https://www.twitterspacegpt.com/downloaders"

        # Option 1: If they have an API
        # response = requests.post(url + "/api/submit", json={
        #     "space_url": space_url,
        #     "email": email
        # })

        # Option 2: Simulate form submission (requires inspecting actual form)
        # response = requests.post(url, data={
        #     "url": space_url,
        #     "email": email
        # })

        print("\n⚠️  MANUAL STEP REQUIRED:")
        print("   Please submit manually at: https://www.twitterspacegpt.com/downloaders")
        print(f"   Space URL: {space_url}")
        print(f"   Email: {email}")
        print("\n   Press Enter when done...")
        input()

        return True

    def connect_to_email(self):
        """Connect to email via IMAP"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            return mail
        except Exception as e:
            print(f"❌ Error conectando a email: {e}")
            return None

    def wait_for_download_email(self, mail, timeout_minutes=30, check_interval=60):
        """
        Monitor inbox for download email from TwitterSpaceGPT

        Args:
            mail: IMAP connection
            timeout_minutes: Maximum time to wait
            check_interval: Seconds between checks

        Returns:
            str: Download link or None
        """
        print(f"\n📧 Monitoreando correo...")
        print(f"   Timeout: {timeout_minutes} minutos")
        print(f"   Revisando cada {check_interval} segundos")

        start_time = datetime.now()
        timeout = timedelta(minutes=timeout_minutes)

        while datetime.now() - start_time < timeout:
            try:
                # Select inbox
                mail.select("INBOX")

                # Search for emails from TwitterSpaceGPT
                # Adjust search criteria based on actual emails
                since_date = (datetime.now() - timedelta(minutes=30)).strftime("%d-%b-%Y")
                result, data = mail.search(None, f'(FROM "twitterspacegpt.com" SINCE {since_date})')

                if result == "OK":
                    email_ids = data[0].split()

                    if email_ids:
                        # Check most recent email
                        latest_email_id = email_ids[-1]
                        result, msg_data = mail.fetch(latest_email_id, "(RFC822)")

                        if result == "OK":
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)

                            # Extract download link
                            download_link = self.extract_download_link(email_message)

                            if download_link:
                                print(f"\n✅ Link de descarga encontrado!")
                                return download_link

                # Wait before next check
                elapsed = (datetime.now() - start_time).seconds
                remaining = (timeout_minutes * 60) - elapsed
                print(f"   ⏳ Esperando... ({remaining//60}m {remaining%60}s restantes)", end="\r")
                time.sleep(check_interval)

            except Exception as e:
                print(f"\n⚠️  Error revisando email: {e}")
                time.sleep(check_interval)

        print(f"\n⏰ Timeout alcanzado ({timeout_minutes} minutos)")
        return None

    def extract_download_link(self, email_message):
        """
        Extract download link from email

        Args:
            email_message: Email message object

        Returns:
            str: Download link or None
        """
        download_link = None

        # Check if email is multipart
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    body = part.get_payload(decode=True).decode()
                    download_link = self.find_link_in_html(body)
                    if download_link:
                        break
        else:
            body = email_message.get_payload(decode=True).decode()
            download_link = self.find_link_in_html(body)

        return download_link

    def find_link_in_html(self, html_content):
        """
        Find download link in HTML content

        Args:
            html_content: HTML string

        Returns:
            str: Download link or None
        """
        # Pattern to match download links
        # Adjust based on actual email format
        patterns = [
            r'href="(https?://[^"]*download[^"]*\.mp3[^"]*)"',
            r'href="(https?://[^"]*\.mp3[^"]*)"',
            r'href="(https?://twitterspacegpt\.com/[^"]*)"',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                return matches[0]

        return None

    def download_mp3(self, url, output_path):
        """
        Download MP3 file from URL

        Args:
            url: Download URL
            output_path: Path to save file

        Returns:
            bool: Success status
        """
        try:
            print(f"\n⬇️  Descargando MP3...")
            print(f"   URL: {url}")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Progress bar
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"   Progreso: {percent:.1f}%", end="\r")

            print(f"\n✅ Descarga completada: {output_path}")
            return True

        except Exception as e:
            print(f"\n❌ Error descargando MP3: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Auto-download Space MP3 from TwitterSpaceGPT"
    )
    parser.add_argument(
        "space_url",
        help="URL of the Twitter Space"
    )
    parser.add_argument(
        "-e", "--episode",
        required=True,
        help="Episode number"
    )
    parser.add_argument(
        "--email",
        help="Email to receive download link (default: from .env)",
        default=None
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout in minutes (default: 30)"
    )
    parser.add_argument(
        "--skip-submit",
        action="store_true",
        help="Skip submission step (if already submitted manually)"
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Automatically process episode after download"
    )

    args = parser.parse_args()

    # Get email credentials
    email_address = args.email or os.getenv("DOWNLOAD_EMAIL")
    email_password = os.getenv("DOWNLOAD_EMAIL_PASSWORD")

    if not email_address or not email_password:
        print("❌ Error: Email credentials not found")
        print("Set DOWNLOAD_EMAIL and DOWNLOAD_EMAIL_PASSWORD in config/.env")
        sys.exit(1)

    print("\n" + "="*60)
    print("BandaWeb3 - Auto Download Agent")
    print("="*60)
    print(f"Episode: #{args.episode}")
    print(f"Space URL: {args.space_url}")
    print(f"Email: {email_address}")
    print("="*60 + "\n")

    # Initialize agent
    agent = SpaceDownloadAgent(email_address, email_password)

    # Step 1: Submit to TwitterSpaceGPT
    if not args.skip_submit:
        agent.submit_to_twitterspacegpt(args.space_url, email_address)
    else:
        print("⏭️  Saltando paso de envío (--skip-submit)")

    # Step 2: Connect to email
    mail = agent.connect_to_email()
    if not mail:
        print("❌ No se pudo conectar al correo")
        sys.exit(1)

    print("✅ Conectado al correo")

    # Step 3: Wait for download email
    download_link = agent.wait_for_download_email(mail, args.timeout)

    if not download_link:
        print("\n❌ No se encontró link de descarga")
        print("Opciones:")
        print("1. Revisar manualmente tu correo")
        print("2. Aumentar timeout: --timeout 60")
        print("3. Descargar manualmente del correo")
        sys.exit(1)

    # Step 4: Download MP3
    date = datetime.now().strftime("%Y-%m-%d")
    episode_dir = Path(f"../E{args.episode}_{date}")
    episode_dir.mkdir(parents=True, exist_ok=True)
    (episode_dir / "raw").mkdir(exist_ok=True)

    output_path = episode_dir / "raw" / "audio.mp3"

    if agent.download_mp3(download_link, output_path):
        print(f"\n{'='*60}")
        print("✅ DESCARGA COMPLETADA")
        print(f"{'='*60}")
        print(f"Archivo: {output_path}")
        print(f"Tamaño: {output_path.stat().st_size / 1024 / 1024:.2f} MB")

        # Step 5: Optionally process episode
        if args.process:
            print(f"\n🚀 Iniciando procesamiento automático...")
            script_path = Path(__file__).parent / "process_episode.sh"

            try:
                subprocess.run([
                    str(script_path),
                    args.episode,
                    str(output_path)
                ], check=True)
                print("\n✅ Procesamiento completado!")
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error en procesamiento: {e}")
        else:
            print(f"\nPróximo paso:")
            print(f"  ./scripts/process_episode.sh {args.episode} {output_path}")

    else:
        print("\n❌ Descarga falló")
        sys.exit(1)


if __name__ == "__main__":
    main()

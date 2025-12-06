#!/usr/bin/env python3
"""
BandaWeb3 - Space Audio Downloader
Downloads audio from X (Twitter) Spaces using twitter-api-client
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../config/.env")

def setup_output_directory(episode_number, date_str):
    """
    Create organized directory structure for the episode

    Args:
        episode_number (str): Episode number (e.g., "073")
        date_str (str): Date string (e.g., "2024-12-03")

    Returns:
        Path: Path to the episode directory
    """
    base_path = Path(os.getenv("BASE_STORAGE_PATH", "."))
    episode_dir = base_path / f"E{episode_number}_{date_str}"

    # Create subdirectories
    episode_dir.mkdir(parents=True, exist_ok=True)
    (episode_dir / "raw").mkdir(exist_ok=True)
    (episode_dir / "transcripts").mkdir(exist_ok=True)
    (episode_dir / "content").mkdir(exist_ok=True)
    (episode_dir / "media").mkdir(exist_ok=True)

    return episode_dir


def download_space_audio_method1(space_url):
    """
    Method 1: Using twitter-api-client library (recommended)

    NOTE: This requires installing the library:
    pip install twitter-api-client

    Args:
        space_url (str): URL of the Space

    Returns:
        str: Path to downloaded audio file
    """
    try:
        from twitter.scraper import Scraper

        # Initialize scraper (may need cookies for authentication)
        scraper = Scraper()

        # Extract space ID from URL
        space_id = space_url.split('/')[-1].split('?')[0]

        print(f"Downloading Space: {space_id}")

        # Download audio
        # Note: This is a placeholder - actual implementation depends on library version
        audio_data = scraper.spaces_live(space_id)

        # Save audio file
        output_path = f"space_{space_id}.m4a"
        with open(output_path, 'wb') as f:
            f.write(audio_data)

        print(f"✓ Audio downloaded: {output_path}")
        return output_path

    except ImportError:
        print("ERROR: twitter-api-client not installed")
        print("Install with: pip install git+https://github.com/trevorhobenshield/twitter-api-client")
        return None
    except Exception as e:
        print(f"ERROR downloading audio: {e}")
        return None


def download_space_audio_method2(space_url):
    """
    Method 2: Using yt-dlp (alternative method)

    NOTE: This requires installing yt-dlp:
    pip install yt-dlp

    Args:
        space_url (str): URL of the Space

    Returns:
        str: Path to downloaded audio file
    """
    try:
        import yt_dlp

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(id)s.%(ext)s',
        }

        print(f"Downloading Space with yt-dlp: {space_url}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(space_url, download=True)
            filename = ydl.prepare_filename(info)
            # Replace extension with mp3
            audio_path = filename.rsplit('.', 1)[0] + '.mp3'

        print(f"✓ Audio downloaded: {audio_path}")
        return audio_path

    except ImportError:
        print("ERROR: yt-dlp not installed")
        print("Install with: pip install yt-dlp")
        return None
    except Exception as e:
        print(f"ERROR downloading with yt-dlp: {e}")
        return None


def save_metadata(episode_dir, space_url, episode_number, metadata=None):
    """
    Save episode metadata to JSON file

    Args:
        episode_dir (Path): Episode directory
        space_url (str): Space URL
        episode_number (str): Episode number
        metadata (dict, optional): Additional metadata
    """
    metadata_dict = {
        "episode_number": episode_number,
        "space_url": space_url,
        "download_date": datetime.now().isoformat(),
        "status": "downloaded",
    }

    if metadata:
        metadata_dict.update(metadata)

    metadata_path = episode_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata_dict, f, indent=2, ensure_ascii=False)

    print(f"✓ Metadata saved: {metadata_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Download audio from X (Twitter) Space"
    )
    parser.add_argument(
        "space_url",
        help="URL of the Space to download"
    )
    parser.add_argument(
        "-e", "--episode",
        required=True,
        help="Episode number (e.g., 073)"
    )
    parser.add_argument(
        "-m", "--method",
        choices=["twitter-api", "yt-dlp", "manual"],
        default="twitter-api",
        help="Download method to use"
    )

    args = parser.parse_args()

    # Setup episode directory
    date_str = datetime.now().strftime("%Y-%m-%d")
    episode_dir = setup_output_directory(args.episode, date_str)

    print(f"\n{'='*60}")
    print(f"BandaWeb3 Space Downloader")
    print(f"{'='*60}")
    print(f"Episode: #{args.episode}")
    print(f"Space URL: {args.space_url}")
    print(f"Output Directory: {episode_dir}")
    print(f"Method: {args.method}")
    print(f"{'='*60}\n")

    # Download audio based on selected method
    audio_path = None

    if args.method == "twitter-api":
        audio_path = download_space_audio_method1(args.space_url)
    elif args.method == "yt-dlp":
        audio_path = download_space_audio_method2(args.space_url)
    elif args.method == "manual":
        print("\nMANUAL MODE:")
        print("1. Go to X (Twitter) as the Space host")
        print("2. Open the Space page")
        print("3. Download the recording (available for 30 days)")
        print(f"4. Save the file to: {episode_dir / 'raw' / 'audio.mp3'}")
        print("\nAfter downloading manually, run the transcription script.")
        return

    # Move audio to episode directory if downloaded
    if audio_path and Path(audio_path).exists():
        final_path = episode_dir / "raw" / "audio.mp3"
        Path(audio_path).rename(final_path)
        print(f"\n✓ Audio moved to: {final_path}")

        # Save metadata
        save_metadata(episode_dir, args.space_url, args.episode)

        print(f"\n{'='*60}")
        print("SUCCESS! Audio downloaded and organized.")
        print(f"{'='*60}")
        print(f"\nNext steps:")
        print(f"1. Transcribe audio: python scripts/transcribe_audio.py {final_path}")
        print(f"2. Generate content: python scripts/generate_content.py {episode_dir}")

    else:
        print("\nERROR: Audio download failed.")
        print("\nAlternative: Use manual download method:")
        print(f"  python {__file__} {args.space_url} -e {args.episode} -m manual")


if __name__ == "__main__":
    main()

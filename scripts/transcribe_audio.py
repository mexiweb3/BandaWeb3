#!/usr/bin/env python3
"""
BandaWeb3 - Audio Transcription Script
Transcribes audio files using OpenAI Whisper API (cloud)
Much faster than local Whisper and includes timestamps
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv(dotenv_path="../config/.env")

# Configure OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def transcribe_audio_whisper_api(audio_path, language="es"):
    """
    Transcribe audio file using OpenAI Whisper API

    Args:
        audio_path (str or Path): Path to audio file
        language (str): Language code (default: "es" for Spanish)

    Returns:
        dict: Transcription result with text and segments
    """
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Transcribing: {audio_path.name}")
    print(f"File size: {audio_path.stat().st_size / 1024 / 1024:.2f} MB")

    # Check file size (Whisper API limit is 25 MB)
    file_size_mb = audio_path.stat().st_size / 1024 / 1024
    if file_size_mb > 25:
        print(f"\n⚠️  WARNING: File size ({file_size_mb:.2f} MB) exceeds 25 MB limit")
        print("Consider splitting the file or compressing it first")
        return None

    try:
        # Open audio file
        with open(audio_path, "rb") as audio_file:
            print("\nSending to Whisper API...")

            # Call Whisper API with verbose_json for timestamps
            transcript = client.audio.transcriptions.create(
                model=os.getenv("WHISPER_MODEL", "whisper-1"),
                file=audio_file,
                language=language,
                response_format="verbose_json",  # Includes timestamps
                temperature=float(os.getenv("WHISPER_TEMPERATURE", 0.2))
            )

        print("✓ Transcription completed!")

        # Parse response
        result = {
            "text": transcript.text,
            "language": transcript.language,
            "duration": transcript.duration,
            "segments": []
        }

        # Add segments if available
        if hasattr(transcript, 'segments') and transcript.segments:
            result["segments"] = [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text
                }
                for seg in transcript.segments
            ]

        return result

    except openai.APIError as e:
        print(f"\n❌ OpenAI API Error: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Error during transcription: {e}")
        return None


def save_transcription(result, output_dir, format="all"):
    """
    Save transcription in multiple formats

    Args:
        result (dict): Transcription result
        output_dir (Path): Output directory
        format (str): Output format ("txt", "json", "srt", "all")

    Returns:
        dict: Paths to saved files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = {}

    # Save as plain text
    if format in ["txt", "all"]:
        txt_path = output_dir / "transcription.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        saved_files["txt"] = txt_path
        print(f"✓ Saved TXT: {txt_path}")

    # Save as JSON (includes timestamps)
    if format in ["json", "all"]:
        json_path = output_dir / "transcription.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        saved_files["json"] = json_path
        print(f"✓ Saved JSON: {json_path}")

    # Save as SRT (subtitle format with timestamps)
    if format in ["srt", "all"] and result.get("segments"):
        srt_path = output_dir / "transcription.srt"
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result["segments"], 1):
                # SRT format
                start_time = format_timestamp_srt(segment["start"])
                end_time = format_timestamp_srt(segment["end"])
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        saved_files["srt"] = srt_path
        print(f"✓ Saved SRT: {srt_path}")

    return saved_files


def format_timestamp_srt(seconds):
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)

    Args:
        seconds (float): Time in seconds

    Returns:
        str: Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_stats(result):
    """
    Generate statistics about the transcription

    Args:
        result (dict): Transcription result

    Returns:
        dict: Statistics
    """
    stats = {
        "duration_seconds": result.get("duration", 0),
        "duration_formatted": format_duration(result.get("duration", 0)),
        "total_words": len(result["text"].split()),
        "total_characters": len(result["text"]),
        "language": result.get("language", "unknown"),
        "segments_count": len(result.get("segments", [])),
    }

    return stats


def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio using OpenAI Whisper API"
    )
    parser.add_argument(
        "audio_file",
        help="Path to audio file (MP3, M4A, WAV, etc.)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: same as audio file)",
        default=None
    )
    parser.add_argument(
        "-l", "--language",
        help="Language code (default: es for Spanish)",
        default="es"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["txt", "json", "srt", "all"],
        default="all",
        help="Output format(s)"
    )

    args = parser.parse_args()

    # Validate API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please set it in config/.env file")
        sys.exit(1)

    # Set output directory
    audio_path = Path(args.audio_file)
    if args.output:
        output_dir = Path(args.output)
    else:
        # Use transcripts subdirectory if it exists, otherwise same directory
        parent_dir = audio_path.parent.parent
        if (parent_dir / "transcripts").exists():
            output_dir = parent_dir / "transcripts"
        else:
            output_dir = audio_path.parent

    print(f"\n{'='*60}")
    print(f"BandaWeb3 Audio Transcription")
    print(f"{'='*60}")
    print(f"Audio file: {audio_path}")
    print(f"Output directory: {output_dir}")
    print(f"Language: {args.language}")
    print(f"Format: {args.format}")
    print(f"{'='*60}\n")

    # Transcribe
    result = transcribe_audio_whisper_api(audio_path, args.language)

    if result:
        # Save transcription
        saved_files = save_transcription(result, output_dir, args.format)

        # Generate and display stats
        stats = generate_stats(result)

        print(f"\n{'='*60}")
        print("TRANSCRIPTION STATISTICS")
        print(f"{'='*60}")
        print(f"Duration: {stats['duration_formatted']}")
        print(f"Language: {stats['language']}")
        print(f"Words: {stats['total_words']:,}")
        print(f"Characters: {stats['total_characters']:,}")
        print(f"Segments: {stats['segments_count']}")
        print(f"{'='*60}\n")

        print("✅ SUCCESS! Transcription completed.")
        print(f"\nFiles saved in: {output_dir}")
        for format_type, path in saved_files.items():
            print(f"  - {format_type.upper()}: {path.name}")

        print(f"\nNext steps:")
        print(f"1. Review transcription: {saved_files.get('txt', 'N/A')}")
        print(f"2. Generate content: python scripts/generate_content.py {output_dir.parent}")
    else:
        print("\n❌ Transcription failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

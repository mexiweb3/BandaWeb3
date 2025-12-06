#!/usr/bin/env python3
"""
BandaWeb3 - Content Generation Script
Generates social media content from transcriptions using Claude API
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv(dotenv_path="../config/.env")

# Configure Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


PROMPTS = {
    "thread": """Eres un experto en crear hilos virales para X (Twitter) sobre tecnología blockchain y Web3.

Analiza la siguiente transcripción de un Space de BandaWeb3 y crea un hilo atractivo de máximo 10 tweets.

REGLAS:
- Cada tweet debe tener máximo 280 caracteres
- Primer tweet: Hook potente que capte atención
- Incluir emojis relevantes (sin exagerar)
- Usar formato de hilos numerado (1/10, 2/10, etc.)
- Destacar insights clave, datos importantes o frases memorables
- Estilo: Educativo pero conversacional, profesional pero accesible
- Incluir hashtags relevantes solo en el último tweet: #BandaWeb3 #Web3 #Blockchain

TRANSCRIPCIÓN:
{transcript}

METADATA:
Episode: #{episode_number}
Título: {title}

Genera el hilo en formato JSON:
{{
  "tweets": [
    {{
      "number": 1,
      "text": "texto del tweet",
      "hashtags": []
    }},
    ...
  ]
}}""",

    "article": """Eres un escritor experto en tecnología blockchain que crea artículos detallados y educativos.

Analiza la siguiente transcripción de un Space de BandaWeb3 y crea un artículo largo y bien estructurado.

REQUISITOS:
- Título atractivo y claro
- Introducción que enganche
- Secciones bien organizadas con subtítulos
- Explicaciones claras de conceptos técnicos
- Incluir quotes destacados de la conversación
- Conclusión con reflexión o call-to-action
- Longitud: 1000-1500 palabras
- Formato: Markdown
- Estilo: Profesional pero accesible, educativo
- Público objetivo: Personas interesadas en Web3, desde principiantes hasta expertos

TRANSCRIPCIÓN:
{transcript}

METADATA:
Episode: #{episode_number}
Fecha: {date}
Título: {title}

Genera el artículo en formato Markdown.""",

    "linkedin": """Eres un content strategist experto en LinkedIn que crea posts profesionales sobre tecnología.

Analiza la siguiente transcripción de un Space de BandaWeb3 y crea un post para LinkedIn.

REQUISITOS:
- Gancho inicial fuerte (primera línea crítica)
- Longitud: 200-300 palabras
- Párrafos cortos y escaneables
- 3-5 puntos clave o bullet points
- Tono: Profesional, informativo, reflexivo
- Incluir un call-to-action al final
- 3-5 hashtags relevantes al final
- NO usar emojis excesivos
- Enfocarse en insights de negocio o lecciones aprendidas

TRANSCRIPCIÓN:
{transcript}

METADATA:
Episode: #{episode_number}
Título: {title}

Genera el post.""",

    "highlights": """Eres un experto en identificar momentos destacados de podcasts y conversations.

Analiza la siguiente transcripción de un Space de BandaWeb3 e identifica 3-4 momentos CLAVE para crear clips de video.

CRITERIOS para seleccionar momentos:
- Frase impactante o controversial
- Insight valioso o dato sorprendente
- Explicación clara de un concepto complejo
- Historia o anécdota interesante
- Momento viral potencial
- Duración ideal: 15-60 segundos cada clip

Para cada momento destacado, proporciona:
1. Timestamp de inicio y fin
2. Título corto del clip
3. Transcripción exacta del segmento
4. Razón por la que es destacado
5. Speaker (si se identifica)

TRANSCRIPCIÓN CON TIMESTAMPS:
{transcript_with_timestamps}

Genera la respuesta en formato JSON:
{{
  "highlights": [
    {{
      "title": "Título del clip",
      "start_time": "MM:SS",
      "end_time": "MM:SS",
      "duration_seconds": 45,
      "transcript": "texto exacto del segmento",
      "speaker": "nombre o 'unknown'",
      "reason": "por qué es destacado",
      "potential_reach": "high/medium/low"
    }},
    ...
  ]
}}"""
}


def load_transcription(episode_dir):
    """
    Load transcription files from episode directory

    Args:
        episode_dir (Path): Episode directory

    Returns:
        dict: Transcription data
    """
    episode_dir = Path(episode_dir)
    transcripts_dir = episode_dir / "transcripts"

    # Try to load JSON first (has timestamps)
    json_path = transcripts_dir / "transcription.json"
    txt_path = transcripts_dir / "transcription.txt"

    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "text": data["text"],
                "segments": data.get("segments", []),
                "has_timestamps": True
            }
    elif txt_path.exists():
        with open(txt_path, 'r', encoding='utf-8') as f:
            return {
                "text": f.read(),
                "segments": [],
                "has_timestamps": False
            }
    else:
        raise FileNotFoundError(f"No transcription found in {transcripts_dir}")


def load_metadata(episode_dir):
    """Load episode metadata"""
    metadata_path = Path(episode_dir) / "metadata.json"

    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Return default metadata
        return {
            "episode_number": "XXX",
            "title": "BandaWeb3 Space",
            "date": datetime.now().strftime("%Y-%m-%d")
        }


def generate_content_claude(prompt, max_tokens=4096):
    """
    Generate content using Claude API

    Args:
        prompt (str): The prompt to send to Claude
        max_tokens (int): Maximum tokens in response

    Returns:
        str: Generated content
    """
    try:
        message = client.messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        return None


def generate_thread(transcript, metadata):
    """Generate X thread"""
    print("\n📱 Generating X thread...")

    prompt = PROMPTS["thread"].format(
        transcript=transcript["text"][:15000],  # Limit for API
        episode_number=metadata.get("episode_number", "XXX"),
        title=metadata.get("title", "BandaWeb3 Space")
    )

    response = generate_content_claude(prompt)

    if response:
        print("✓ Thread generated!")
        return response
    return None


def generate_article(transcript, metadata):
    """Generate long-form article"""
    print("\n📝 Generating article...")

    prompt = PROMPTS["article"].format(
        transcript=transcript["text"],
        episode_number=metadata.get("episode_number", "XXX"),
        date=metadata.get("date", datetime.now().strftime("%Y-%m-%d")),
        title=metadata.get("title", "BandaWeb3 Space")
    )

    response = generate_content_claude(prompt, max_tokens=6000)

    if response:
        print("✓ Article generated!")
        return response
    return None


def generate_linkedin_post(transcript, metadata):
    """Generate LinkedIn post"""
    print("\n💼 Generating LinkedIn post...")

    prompt = PROMPTS["linkedin"].format(
        transcript=transcript["text"][:10000],
        episode_number=metadata.get("episode_number", "XXX"),
        title=metadata.get("title", "BandaWeb3 Space")
    )

    response = generate_content_claude(prompt)

    if response:
        print("✓ LinkedIn post generated!")
        return response
    return None


def generate_highlights(transcript, metadata):
    """Identify highlight moments for video clips"""
    print("\n🎬 Identifying highlight moments...")

    # Format transcript with timestamps if available
    if transcript["has_timestamps"] and transcript["segments"]:
        formatted_transcript = "\n\n".join([
            f"[{format_timestamp(seg['start'])} - {format_timestamp(seg['end'])}] {seg['text']}"
            for seg in transcript["segments"]
        ])
    else:
        formatted_transcript = transcript["text"]
        print("⚠️  No timestamps available - results may be less accurate")

    prompt = PROMPTS["highlights"].format(
        transcript_with_timestamps=formatted_transcript[:20000]
    )

    response = generate_content_claude(prompt, max_tokens=3000)

    if response:
        print("✓ Highlights identified!")
        return response
    return None


def format_timestamp(seconds):
    """Format seconds to MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def save_generated_content(content_dict, output_dir):
    """
    Save all generated content

    Args:
        content_dict (dict): Dictionary with all generated content
        output_dir (Path): Output directory
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for content_type, content in content_dict.items():
        if content:
            if content_type == "thread":
                path = output_dir / "thread_x.json"
                # Try to parse as JSON, otherwise save as text
                try:
                    # Extract JSON from markdown code block if present
                    if "```json" in content:
                        json_str = content.split("```json")[1].split("```")[0].strip()
                        data = json.loads(json_str)
                    else:
                        data = json.loads(content)

                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except:
                    path = output_dir / "thread_x.txt"
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)

            elif content_type == "article":
                path = output_dir / "article.md"
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

            elif content_type == "linkedin":
                path = output_dir / "post_linkedin.txt"
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

            elif content_type == "highlights":
                path = output_dir / "video_highlights.json"
                try:
                    if "```json" in content:
                        json_str = content.split("```json")[1].split("```")[0].strip()
                        data = json.loads(json_str)
                    else:
                        data = json.loads(content)

                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                except:
                    path = output_dir / "video_highlights.txt"
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)

            saved_files.append(path)
            print(f"✓ Saved: {path}")

    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="Generate social media content from transcriptions"
    )
    parser.add_argument(
        "episode_dir",
        help="Path to episode directory"
    )
    parser.add_argument(
        "-t", "--types",
        nargs="+",
        choices=["thread", "article", "linkedin", "highlights", "all"],
        default=["all"],
        help="Content types to generate"
    )

    args = parser.parse_args()

    # Validate API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set it in config/.env file")
        sys.exit(1)

    episode_dir = Path(args.episode_dir)

    if not episode_dir.exists():
        print(f"❌ ERROR: Episode directory not found: {episode_dir}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"BandaWeb3 Content Generator")
    print(f"{'='*60}")
    print(f"Episode directory: {episode_dir}")
    print(f"Content types: {', '.join(args.types)}")
    print(f"{'='*60}\n")

    # Load transcription and metadata
    try:
        transcript = load_transcription(episode_dir)
        metadata = load_metadata(episode_dir)
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

    print(f"Episode #{metadata.get('episode_number', 'XXX')}")
    print(f"Transcription loaded: {len(transcript['text'])} characters")
    print(f"Has timestamps: {transcript['has_timestamps']}")

    # Determine what to generate
    types_to_generate = args.types
    if "all" in types_to_generate:
        types_to_generate = ["thread", "article", "linkedin", "highlights"]

    # Generate content
    generated_content = {}

    if "thread" in types_to_generate:
        generated_content["thread"] = generate_thread(transcript, metadata)

    if "article" in types_to_generate:
        generated_content["article"] = generate_article(transcript, metadata)

    if "linkedin" in types_to_generate:
        generated_content["linkedin"] = generate_linkedin_post(transcript, metadata)

    if "highlights" in types_to_generate:
        generated_content["highlights"] = generate_highlights(transcript, metadata)

    # Save all generated content
    output_dir = episode_dir / "content"
    saved_files = save_generated_content(generated_content, output_dir)

    print(f"\n{'='*60}")
    print("✅ CONTENT GENERATION COMPLETE!")
    print(f"{'='*60}")
    print(f"\nGenerated {len(saved_files)} files in: {output_dir}")
    print("\nNext steps:")
    print("1. Review generated content")
    print("2. Edit/approve as needed")
    print("3. Use n8n workflow to schedule publications")
    print("4. Generate video clips (if highlights were created)")


if __name__ == "__main__":
    main()

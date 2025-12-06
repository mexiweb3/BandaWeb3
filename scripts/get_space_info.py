#!/usr/bin/env python3
"""
BandaWeb3 - Get Space Information
Obtiene metadata de un Space usando X API Pro
"""

import os
import sys
import json
import tweepy
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path="../config/.env")


class SpaceInfoFetcher:
    def __init__(self):
        """Initialize Twitter API client"""
        self.client = tweepy.Client(
            bearer_token=os.getenv("X_BEARER_TOKEN"),
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
            wait_on_rate_limit=True
        )

    def extract_space_id(self, space_url):
        """Extract Space ID from URL"""
        # URL format: https://twitter.com/i/spaces/1ABC...
        if 'spaces/' in space_url:
            return space_url.split('spaces/')[-1].split('?')[0]
        return space_url

    def get_space_info(self, space_id):
        """
        Get Space information from X API

        Returns:
            dict: Space metadata
        """
        try:
            # X API v2 - Get Space
            response = self.client.get_space(
                id=space_id,
                space_fields=[
                    'host_ids',
                    'created_at',
                    'ended_at',
                    'participant_count',
                    'speaker_ids',
                    'started_at',
                    'title',
                    'topic_ids',
                    'updated_at',
                    'scheduled_start',
                    'is_ticketed',
                    'state'
                ],
                expansions=['host_ids', 'speaker_ids']
            )

            space = response.data

            # Get host and speaker info
            users = {}
            if response.includes and 'users' in response.includes:
                for user in response.includes['users']:
                    users[user.id] = {
                        'username': user.username,
                        'name': user.name
                    }

            # Build metadata
            metadata = {
                'space_id': space.id,
                'title': space.title,
                'state': space.state,
                'created_at': str(space.created_at) if space.created_at else None,
                'started_at': str(space.started_at) if space.started_at else None,
                'ended_at': str(space.ended_at) if space.ended_at else None,
                'participant_count': space.participant_count,
                'hosts': [users.get(host_id, {'username': host_id}) for host_id in (space.host_ids or [])],
                'speakers': [users.get(speaker_id, {'username': speaker_id}) for speaker_id in (space.speaker_ids or [])],
                'fetched_at': datetime.now().isoformat()
            }

            return metadata

        except tweepy.errors.TweepyException as e:
            print(f"❌ Error obteniendo info del Space: {e}")
            return None

    def format_duration(self, started_at, ended_at):
        """Calculate and format duration"""
        if not started_at or not ended_at:
            return "Desconocida"

        try:
            start = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
            duration = end - start

            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60

            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Error calculando"


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Obtener información de un Space"
    )
    parser.add_argument(
        "space_url",
        help="URL del Space (ej: https://twitter.com/i/spaces/1ABC...)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Guardar metadata en archivo JSON"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Mostrar output en formato JSON"
    )

    args = parser.parse_args()

    # Initialize fetcher
    fetcher = SpaceInfoFetcher()

    # Extract Space ID
    space_id = fetcher.extract_space_id(args.space_url)
    print(f"🔍 Obteniendo info del Space: {space_id}")

    # Get Space info
    metadata = fetcher.get_space_info(space_id)

    if not metadata:
        print("❌ No se pudo obtener información del Space")
        sys.exit(1)

    # Output
    if args.json:
        # JSON output
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
    else:
        # Formatted output
        print("\n" + "=" * 60)
        print("📊 INFORMACIÓN DEL SPACE")
        print("=" * 60)
        print(f"Título: {metadata['title']}")
        print(f"Estado: {metadata['state']}")
        print(f"Participantes: {metadata['participant_count']}")

        if metadata['hosts']:
            print(f"\nHosts:")
            for host in metadata['hosts']:
                print(f"  • @{host['username']} ({host.get('name', 'N/A')})")

        if metadata['speakers']:
            print(f"\nSpeakers ({len(metadata['speakers'])}):")
            for speaker in metadata['speakers'][:5]:  # Show first 5
                print(f"  • @{speaker['username']} ({speaker.get('name', 'N/A')})")
            if len(metadata['speakers']) > 5:
                print(f"  ... y {len(metadata['speakers']) - 5} más")

        duration = fetcher.format_duration(
            metadata.get('started_at'),
            metadata.get('ended_at')
        )
        print(f"\nDuración: {duration}")

        if metadata.get('started_at'):
            print(f"Inicio: {metadata['started_at']}")
        if metadata.get('ended_at'):
            print(f"Fin: {metadata['ended_at']}")

    # Save to file
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Metadata guardada en: {output_path}")


if __name__ == "__main__":
    main()

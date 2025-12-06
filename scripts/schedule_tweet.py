#!/usr/bin/env python3
"""
BandaWeb3 - Schedule Tweet
Programa tweets para publicación futura (requiere cron o n8n)
"""

import os
import sys
import json
import tweepy
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../config/.env")


class TweetScheduler:
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

        self.schedule_file = Path("../config/scheduled_tweets.json")

    def load_schedule(self):
        """Load scheduled tweets from file"""
        if not self.schedule_file.exists():
            return []

        with open(self.schedule_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_schedule(self, schedule):
        """Save schedule to file"""
        self.schedule_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)

    def add_to_schedule(self, content, scheduled_time, metadata=None):
        """
        Add tweet to schedule

        Args:
            content: Tweet content
            scheduled_time: datetime object or ISO string
            metadata: Additional metadata (optional)
        """
        schedule = self.load_schedule()

        # Convert to ISO string if datetime
        if isinstance(scheduled_time, datetime):
            scheduled_time = scheduled_time.isoformat()

        tweet_data = {
            'id': len(schedule) + 1,
            'content': content,
            'scheduled_time': scheduled_time,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        schedule.append(tweet_data)
        self.save_schedule(schedule)

        print(f"✅ Tweet programado para: {scheduled_time}")
        return tweet_data

    def publish_pending_tweets(self):
        """Publish tweets that are due"""
        schedule = self.load_schedule()
        now = datetime.now()

        published_count = 0

        for tweet in schedule:
            if tweet['status'] != 'pending':
                continue

            scheduled_time = datetime.fromisoformat(tweet['scheduled_time'])

            if scheduled_time <= now:
                try:
                    # Publish tweet
                    response = self.client.create_tweet(text=tweet['content'])
                    tweet_id = response.data['id']

                    # Update status
                    tweet['status'] = 'published'
                    tweet['published_at'] = now.isoformat()
                    tweet['tweet_id'] = tweet_id

                    print(f"✅ Tweet publicado: {tweet_id}")
                    print(f"   Contenido: {tweet['content'][:60]}...")

                    published_count += 1

                except tweepy.errors.TweepyException as e:
                    print(f"❌ Error publicando tweet: {e}")
                    tweet['status'] = 'failed'
                    tweet['error'] = str(e)

        # Save updated schedule
        if published_count > 0:
            self.save_schedule(schedule)

        return published_count

    def list_scheduled(self, status='pending'):
        """List scheduled tweets"""
        schedule = self.load_schedule()

        filtered = [t for t in schedule if t['status'] == status]

        print(f"\n📋 Tweets programados ({status}):")
        print("=" * 60)

        for tweet in filtered:
            print(f"\nID: {tweet['id']}")
            print(f"Programado: {tweet['scheduled_time']}")
            print(f"Contenido: {tweet['content'][:80]}...")
            print("-" * 60)

        return filtered

    def delete_scheduled(self, tweet_id):
        """Delete scheduled tweet"""
        schedule = self.load_schedule()

        updated_schedule = [t for t in schedule if t['id'] != tweet_id]

        if len(updated_schedule) < len(schedule):
            self.save_schedule(updated_schedule)
            print(f"✅ Tweet {tweet_id} eliminado del schedule")
            return True
        else:
            print(f"❌ Tweet {tweet_id} no encontrado")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Programar tweets para publicación futura"
    )

    subparsers = parser.add_subparsers(dest='command', help='Comandos')

    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Programar nuevo tweet')
    schedule_parser.add_argument('content', help='Contenido del tweet')
    schedule_parser.add_argument(
        '--time',
        required=True,
        help='Hora de publicación (formato: YYYY-MM-DD HH:MM o "in 2h")'
    )
    schedule_parser.add_argument('--episode', help='Número de episodio')

    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publicar tweets pendientes')

    # List command
    list_parser = subparsers.add_parser('list', help='Listar tweets programados')
    list_parser.add_argument(
        '--status',
        default='pending',
        choices=['pending', 'published', 'failed', 'all'],
        help='Filtrar por estado'
    )

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Eliminar tweet programado')
    delete_parser.add_argument('id', type=int, help='ID del tweet')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    scheduler = TweetScheduler()

    if args.command == 'schedule':
        # Parse time
        if args.time.startswith('in '):
            # Relative time (e.g., "in 2h", "in 30m")
            time_str = args.time.replace('in ', '')
            if 'h' in time_str:
                hours = int(time_str.replace('h', ''))
                scheduled_time = datetime.now() + timedelta(hours=hours)
            elif 'm' in time_str:
                minutes = int(time_str.replace('m', ''))
                scheduled_time = datetime.now() + timedelta(minutes=minutes)
            else:
                print("❌ Formato de tiempo relativo inválido. Usa: 'in 2h' o 'in 30m'")
                sys.exit(1)
        else:
            # Absolute time
            scheduled_time = datetime.fromisoformat(args.time)

        metadata = {}
        if args.episode:
            metadata['episode'] = args.episode

        scheduler.add_to_schedule(args.content, scheduled_time, metadata)

    elif args.command == 'publish':
        count = scheduler.publish_pending_tweets()
        print(f"\n✅ Total publicados: {count}")

    elif args.command == 'list':
        status = None if args.status == 'all' else args.status
        scheduler.list_scheduled(status)

    elif args.command == 'delete':
        scheduler.delete_scheduled(args.id)


if __name__ == "__main__":
    main()

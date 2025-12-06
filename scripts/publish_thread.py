#!/usr/bin/env python3
"""
BandaWeb3 - Auto-Publish Thread to X
Publica automáticamente hilos generados en X (Twitter)
"""

import os
import sys
import json
import time
import tweepy
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../config/.env")


class TwitterThreadPublisher:
    def __init__(self):
        """Initialize Twitter API client"""
        # X API v2 credentials
        self.client = tweepy.Client(
            bearer_token=os.getenv("X_BEARER_TOKEN"),
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
            wait_on_rate_limit=True
        )

    def load_thread(self, thread_file):
        """Load thread from JSON file"""
        with open(thread_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('thread', [])

    def publish_thread(self, thread_data, delay=3):
        """
        Publish thread to X

        Args:
            thread_data: List of tweet objects
            delay: Seconds to wait between tweets (default: 3)

        Returns:
            List of tweet IDs
        """
        tweet_ids = []
        previous_tweet_id = None

        print(f"\n🐦 Publicando hilo de {len(thread_data)} tweets...")
        print("=" * 60)

        for i, tweet in enumerate(thread_data, 1):
            content = tweet.get('content', '')

            try:
                # Publish tweet
                if previous_tweet_id is None:
                    # First tweet (no reply)
                    response = self.client.create_tweet(text=content)
                else:
                    # Reply to previous tweet
                    response = self.client.create_tweet(
                        text=content,
                        in_reply_to_tweet_id=previous_tweet_id
                    )

                tweet_id = response.data['id']
                tweet_ids.append(tweet_id)
                previous_tweet_id = tweet_id

                print(f"✅ Tweet {i}/{len(thread_data)} publicado")
                print(f"   ID: {tweet_id}")
                print(f"   Preview: {content[:60]}...")

                # Wait before next tweet (avoid rate limits)
                if i < len(thread_data):
                    print(f"   ⏳ Esperando {delay} segundos...")
                    time.sleep(delay)

            except tweepy.errors.TweepyException as e:
                print(f"❌ Error publicando tweet {i}: {e}")
                print(f"   Contenido: {content}")

                # Ask user if they want to continue
                if i < len(thread_data):
                    response = input("\n¿Continuar con siguiente tweet? (y/n): ")
                    if response.lower() != 'y':
                        break

        return tweet_ids

    def get_thread_url(self, first_tweet_id, username=None):
        """Generate URL to view thread"""
        if username is None:
            # Try to get username from API
            try:
                me = self.client.get_me()
                username = me.data.username
            except:
                username = "USERNAME"

        return f"https://twitter.com/{username}/status/{first_tweet_id}"

    def publish_single_tweet(self, content):
        """Publish a single tweet"""
        try:
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            print(f"✅ Tweet publicado: {tweet_id}")
            return tweet_id
        except tweepy.errors.TweepyException as e:
            print(f"❌ Error: {e}")
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Publicar hilo de X automáticamente"
    )
    parser.add_argument(
        "thread_file",
        help="Archivo JSON con el hilo (ej: ../E075_*/content/thread_x.json)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="Segundos entre tweets (default: 3)"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Solo mostrar preview sin publicar"
    )

    args = parser.parse_args()

    # Validate file exists
    if not Path(args.thread_file).exists():
        print(f"❌ Error: Archivo no encontrado: {args.thread_file}")
        sys.exit(1)

    # Initialize publisher
    publisher = TwitterThreadPublisher()

    # Load thread
    thread_data = publisher.load_thread(args.thread_file)

    if not thread_data:
        print("❌ Error: No se encontraron tweets en el archivo")
        sys.exit(1)

    # Preview mode
    if args.preview:
        print(f"\n📋 PREVIEW del hilo ({len(thread_data)} tweets):")
        print("=" * 60)
        for i, tweet in enumerate(thread_data, 1):
            content = tweet.get('content', '')
            chars = len(content)
            print(f"\n{i}/{len(thread_data)} ({chars} chars):")
            print(content)
            print("-" * 60)
        print("\nPara publicar, ejecuta sin --preview")
        sys.exit(0)

    # Confirm publication
    print(f"\n📊 Resumen:")
    print(f"   Total tweets: {len(thread_data)}")
    print(f"   Delay entre tweets: {args.delay}s")
    print(f"   Archivo: {args.thread_file}")
    print()

    response = input("¿Publicar hilo en X? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelado")
        sys.exit(0)

    # Publish thread
    tweet_ids = publisher.publish_thread(thread_data, delay=args.delay)

    # Summary
    print("\n" + "=" * 60)
    print("✅ HILO PUBLICADO")
    print("=" * 60)
    print(f"Total tweets publicados: {len(tweet_ids)}")

    if tweet_ids:
        first_tweet_id = tweet_ids[0]
        thread_url = publisher.get_thread_url(first_tweet_id)
        print(f"\n🔗 Ver hilo completo:")
        print(f"   {thread_url}")

        # Save published info
        thread_dir = Path(args.thread_file).parent
        published_file = thread_dir / "thread_published.json"

        with open(published_file, 'w', encoding='utf-8') as f:
            json.dump({
                'published_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'tweet_ids': tweet_ids,
                'thread_url': thread_url,
                'total_tweets': len(tweet_ids)
            }, f, indent=2)

        print(f"\n💾 Info guardada en: {published_file}")


if __name__ == "__main__":
    main()

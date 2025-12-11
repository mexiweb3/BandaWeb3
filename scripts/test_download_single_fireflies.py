#!/usr/bin/env python3
import os
import requests
import json
from pathlib import Path
import time

# Configuración
ENV_FILE = Path(".env")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"
TARGET_TITLE = "BandaWeb3 - 🎙️ Último Space rumbo a #UnlockSummit2025 😊💜✨🌈"

def load_fireflies_api_key():
    if not ENV_FILE.exists():
        return None
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    if key == 'FIREFLIES_API_KEY':
                        return value.strip()
    return None

def get_all_transcripts(api_key):
    query = """
    query Transcripts {
        transcripts {
            id
            title
            date
            duration
        }
    }
    """
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json={"query": query}, timeout=30)
        if response.status_code == 200:
            return response.json().get('data', {}).get('transcripts', [])
        return []
    except Exception as e:
        print(f"Error getting transcripts: {e}")
        return []

def get_transcript_details(transcript_id, api_key):
    query = """
    query Transcript($transcriptId: String!) {
        transcript(id: $transcriptId) {
            id
            title
            sentences {
                text
                speaker_name
                start_time
            }
        }
    }
    """
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    try:
        response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json={"query": query, "variables": {"transcriptId": transcript_id}}, timeout=60)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting details: {e}")
        return None

def main():
    api_key = load_fireflies_api_key()
    if not api_key:
        print("No API key")
        return

    print(f"Searching for: {TARGET_TITLE}")
    transcripts = get_all_transcripts(api_key)
    
    target = next((t for t in transcripts if t['title'] == TARGET_TITLE), None)
    
    if target:
        print(f"✅ Found transcript ID: {target['id']}")
        print("Downloading details...")
        details = get_transcript_details(target['id'], api_key)
        
        if details and 'errors' in details:
             print(f"❌ GraphQL Errors: {details['errors']}")
        elif details and 'data' in details and details['data']['transcript']['sentences']:
             print("✅ Success! Sentences found.")
             print(f"Count: {len(details['data']['transcript']['sentences'])}")
             print(json.dumps(details['data']['transcript']['sentences'][:2], indent=2))
        else:
             print("⚠️  No sentences found (transcript processing not complete?)")
             print(json.dumps(details, indent=2))
    else:
        print("❌ Transcript not found in list (might still be queued)")

if __name__ == "__main__":
    main()

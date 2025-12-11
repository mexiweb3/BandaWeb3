import os
import requests
import json
from pathlib import Path

ENV_FILE = Path(".env")
GRAPHQL_ENDPOINT = "https://api.fireflies.ai/graphql"

def load_apikey():
    with open(ENV_FILE, 'r') as f:
        for line in f:
            if line.startswith("FIREFLIES_API_KEY="):
                return line.strip().split("=", 1)[1]
    return None

def test_pagination_skip(limit, skip):
    api_key = load_apikey()
    query = """
    query Transcripts($limit: Int, $skip: Int) {
        transcripts(limit: $limit, skip: $skip) {
            id
            title
        }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "query": query,
        "variables": {"limit": limit, "skip": skip}
    }
    
    response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print("Errors:", data['errors'])
        else:
            ts = data['data']['transcripts']
            print(f"Limit: {limit}, Skip: {skip}, Got: {len(ts)}")
            if len(ts) > 0:
                print(f"First ID: {ts[0]['id']}")
    else:
        print(f"HTTP Error: {response.status_code}")

if __name__ == "__main__":
    test_pagination_skip(50, 0)
    test_pagination_skip(50, 50)

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

def fetch_detailed_transcript(transcript_id):
    api_key = load_apikey()
    query = """
    query Transcript($id: String!) {
        transcript(id: $id) {
            id
            title
            date
            duration
            speakers {
                id
                name
            }
            sentences {
                index
                speaker_name
                speaker_id
                text
                raw_text
                start_time
                end_time
                ai_filters {
                    task
                    pricing
                }
            }
        }
    }
    """
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "query": query,
        "variables": {"id": transcript_id}
    }
    
    print(f"Fetching details for ID: {transcript_id}")
    response = requests.post(GRAPHQL_ENDPOINT, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print("Errors:", data['errors'])
        else:
            return data['data']['transcript']
    else:
        print(f"HTTP Error: {response.status_code}")
        return None

if __name__ == "__main__":
    # Using one of the recovered Fireflies IDs (from previous step output)
    # File: 01KC0ME0EMQ0CJD_fireflies.json -> ID: 01KC0ME0EMQ0CJD2N7G2FYWQM3
    # Wait, the ID in the file content (Step 29) was 01KC0ME0EMQ0CJD2N7G2FYWQM3
    # The filename was 01KC0ME0EMQ0CJD. Checking if we can use the short ID or need the long one.
    # The file content showed "id": "01KC0ME0EMQ0CJD2N7G2FYWQM3"
    
    tid = "01KC0ME0EMQ0CJD2N7G2FYWQM3" 
    result = fetch_detailed_transcript(tid)
    
    if result:
        print(json.dumps(result, indent=2))
        
        # Check speakers
        speakers = result.get("speakers", [])
        print(f"\nSpeakers found: {len(speakers)}")
        for s in speakers:
            print(f"- {s}")
            
        # Check first few sentences for speaker info
        sentences = result.get("sentences", [])
        print(f"\nSentences: {len(sentences)}")
        for i in range(min(5, len(sentences))):
            s = sentences[i]
            print(f"Sentence {i}: SpeakerName={s.get('speaker_name')}, SpeakerID={s.get('speaker_id')}")

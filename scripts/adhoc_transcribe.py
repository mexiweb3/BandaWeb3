
import os
import json
import requests
import sys

# Configuration
AUDIO_DIR = "audio"
TRANSCRIPTIONS_DIR = "transcriptions"
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&language=es"

def get_api_key():
    """Retrieves the Deepgram API key from the environment."""
    api_key = os.environ.get("DEEPGRAM_API_KEY")
    if not api_key:
        print("Error: DEEPGRAM_API_KEY environment variable not set.")
        print("Please export DEEPGRAM_API_KEY='your_key_here' and try again.")
        sys.exit(1)
    return api_key

def get_existing_transcriptions(transcriptions_dir):
    """Returns a set of filenames (without extension) that have already been transcribed."""
    existing = set()
    if not os.path.exists(transcriptions_dir):
        os.makedirs(transcriptions_dir)
        return existing
        
    for filename in os.listdir(transcriptions_dir):
        if filename.endswith(".json"):
            existing.add(os.path.splitext(filename)[0])
    return existing

def transcribe_file(filepath, api_key):
    """Transcribes a single audio file using Deepgram."""
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/mp3" 
    }
    
    try:
        with open(filepath, "rb") as audio_file:
            response = requests.post(DEEPGRAM_URL, headers=headers, data=audio_file)
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error transcribing {filepath}: {e}")
        try:
             print(f"Response content: {response.text}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Unexpected error for {filepath}: {e}")
        return None

def main():
    api_key = get_api_key()
    
    # Ensure paths are correct relative to script location if needed, 
    # but assuming script is run from 'shared' directory as per CWD.
    if not os.path.exists(AUDIO_DIR):
        print(f"Error: Audio directory '{AUDIO_DIR}' not found.")
        sys.exit(1)

    existing_transcriptions = get_existing_transcriptions(TRANSCRIPTIONS_DIR)
    
    audio_files = [f for f in os.listdir(AUDIO_DIR) if f.lower().endswith(".mp3")]
    total_files = len(audio_files)
    print(f"Found {total_files} audio files.")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0

    for filename in audio_files:
        file_base = os.path.splitext(filename)[0]
        
        if file_base in existing_transcriptions:
            # print(f"Skipping {filename} (already transcribed)")
            skipped_count += 1
            continue
            
        print(f"Transcribing {filename}...")
        filepath = os.path.join(AUDIO_DIR, filename)
        
        result = transcribe_file(filepath, api_key)
        
        if result:
            output_path = os.path.join(TRANSCRIPTIONS_DIR, f"{file_base}.json")
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Saved transcription to {output_path}")
            processed_count += 1
        else:
            error_count += 1

    print("\nProcessing complete.")
    print(f"Total files: {total_files}")
    print(f"New transcriptions: {processed_count}")
    print(f"Skipped (already exist): {skipped_count}")
    print(f"Errors: {error_count}")

if __name__ == "__main__":
    main()

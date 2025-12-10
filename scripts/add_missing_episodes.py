#!/usr/bin/env python3
import json
import os
import glob
from datetime import datetime

DB_PATH = 'shared/episodes_database.json'
AUDIO_DIR = 'shared/audio'
TRANSCRIPTS_DIR = 'shared/transcriptions'

def load_db():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_existing_ids(data):
    ids = set()
    for ep in data['episodes']:
        # Extract ID from space_url if possible
        if 'space_url' in ep and ep['space_url']:
            parts = ep['space_url'].split('/')
            if parts:
                ids.add(parts[-1])
        
        # Also check spacesdashboard_url
        if 'spacesdashboard_url' in ep and ep['spacesdashboard_url']:
            # https://spacesdashboard.com/space/1kvJpbOrYmDKE/bandaweb3-022-at-ariutokintumi
            parts = ep['spacesdashboard_url'].split('/')
            if len(parts) > 4:
                ids.add(parts[4])
                
        # Also check if 'number' matches ID (for cohosted/hosted without number)
        if 'number' in ep:
            ids.add(str(ep['number']))
            
    return ids

def main():
    data = load_db()
    existing_ids = get_existing_ids(data)
    print(f"INFO: Found {len(existing_ids)} existing episode IDs/Numbers in DB.")
    
    mp3_files = glob.glob(os.path.join(AUDIO_DIR, "*.mp3"))
    added_count = 0
    
    for mp3_path in mp3_files:
        filename = os.path.basename(mp3_path)
        space_id = os.path.splitext(filename)[0]
        
        if space_id in existing_ids:
            continue
            
        print(f"NEW EPISODE FOUND: {space_id}")
        
        # Try to get date from file mod time
        mod_time = os.path.getmtime(mp3_path)
        dt_obj = datetime.fromtimestamp(mod_time)
        date_str = dt_obj.strftime("%Y-%m-%d")
        
        # Try to read transcript for title
        transcript_path = os.path.join(TRANSCRIPTS_DIR, f"{space_id}.txt")
        title = f"Twitter Space {space_id}"
        description = "Descripción pendiente."
        
        if os.path.exists(transcript_path):
            try:
                with open(transcript_path, 'r') as f:
                    content = f.read(1000) # First 1000 chars
                    # Try to find a title line? Hard.
                    # Just check if it's empty
                    if content:
                        description = f"Transcripción disponible. {content[:100]}..."
            except Exception as e:
                print(f"Error reading transcript: {e}")
        
        new_ep = {
            "title": title,
            "date": date_str,
            "duration": "00:00:00", # Unknown
            "host": "@Unknown",
            "guests": [],
            "description": description,
            "topics": [],
            "links": {},
            "id": space_id, # Custom field not usually used but helpful
            "space_url": f"https://x.com/i/spaces/{space_id}",
            "flyer_urls": [],
            "transcript_available": os.path.exists(transcript_path),
            "content_generated": False,
            "type": "hosted", # Default to hosted, user can change
            "status": "archived",
            "number": space_id # Use ID as number for now
        }
        
        data['episodes'].append(new_ep)
        added_count += 1
        print(f" -> Added {space_id} to DB.")
        
    if added_count > 0:
        # Sort by date
        data['episodes'].sort(key=lambda x: x.get('date', '2000-01-01'), reverse=True)
        save_db(data)
        print(f"\nSUCCESS: Added {added_count} new episodes to database.")
    else:
        print("\nNo new episodes to add.")

if __name__ == "__main__":
    main()

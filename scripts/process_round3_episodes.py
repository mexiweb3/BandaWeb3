
import json
import os

DB_PATH = 'shared/episodes_database.json'
TRANSCRIPTS_DIR = 'shared/transcriptions'

NEW_EPISODE_IDS = [
    "1mrxmypkpnZxy", "1BRJjPLOrrNKw", "1LyxBnmXnzWxN", "1mrGmyABrvdGy", 
    "1lPKqBOPjqEGb", "1vOGwMVoyDrxB", "1MnxnMzzjVEJO", "1kvJpvweVXbKE", 
    "1BRKjZoZvpaKw", "1eaKbaomqaRxX", "1eaKbgodvlrGX", "1mnxepBMbBoJX", 
    "1LyGBnYRYEkGN", "1mrGmkgVrnLxy", "1dRKZMQPwZzxB", "1ynJOaWDlYZKR", 
    "1dRJZdoMbrzKB", "1mrxmkPjVPgGy", "1mrGmkAbZYwxy", "1lDGLnBkagkxm", 
    "1ypJdkXPLyNGW"
]

def main():
    print("🔍 Checking 21 new episodes in database...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    found_count = 0
    updated_count = 0
    
    for ep_id in NEW_EPISODE_IDS:
        found = False
        for ep in data['episodes']:
            current_id = ep.get('id')
            if not current_id and ep.get('space_url'):
                 current_id = ep['space_url'].split('/')[-1].split('?')[0]
                 
            if current_id == ep_id:
                found = True
                print(f"✅ Found: {ep.get('title', 'Unknown')} ({ep_id})")
                found_count += 1
                
                if not ep.get('transcript_available'):
                    print(f"   🔄 Enabling transcript...")
                    ep['transcript_available'] = True
                    updated_count += 1
                else:
                    print(f"   ℹ️ Transcript already enabled.")
                break
        
        if not found:
            print(f"⚠️ NOT FOUND in Hosted DB: {ep_id}")

    if updated_count > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Database saved with {updated_count} updates.")
    else:
        print(f"\nℹ️ No updates needed in Hosted DB.")
        
    print(f"📊 Stats: Found {found_count}/{len(NEW_EPISODE_IDS)} in Hosted DB.")

if __name__ == "__main__":
    main()

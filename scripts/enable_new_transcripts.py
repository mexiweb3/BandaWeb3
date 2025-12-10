
import json

DB_PATH = 'shared/episodes_database.json'

def main():
    print("🔄 Updating transcript availability for 6 new episodes...")
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ids_to_update = [
        "1BdGYyrpoyvGX",
        "1LyxBqLjmOoJN",
        "1YqKDoBgNrkxV",
        "1mnxeROErMoKX",
        "1mnxeRwZepQKX",
        "1mrGmklgzAVxy"
    ]
    
    updated_count = 0
    for ep in data['episodes']:
        # Check ID or Space URL
        ep_id = ep.get('id')
        if not ep_id and ep.get('space_url'):
             ep_id = ep['space_url'].split('/')[-1].split('?')[0]
             
        if ep_id in ids_to_update:
            if not ep.get('transcript_available'):
                print(f"✅ Enabling transcript for: {ep.get('title', 'Unknown')} ({ep_id})")
                ep['transcript_available'] = True
                updated_count += 1
            else:
                print(f"ℹ️ Transcript already enabled for: {ep.get('title', 'Unknown')} ({ep_id})")
                
    if updated_count > 0:
        with open(DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Database saved with {updated_count} updates.")
    else:
        print("✅ No updates needed.")

if __name__ == "__main__":
    main()

import json
import os

def generate_report():
    # 1. Get file lists
    audio_path = 'shared/audio'
    trans_path = 'shared/transcriptions'
    
    if os.path.exists(audio_path):
        audio_files = set(f.split('.')[0] for f in os.listdir(audio_path) if f.endswith('.mp3'))
    else:
        audio_files = set()
        
    if os.path.exists(trans_path):
        transcription_files = set(f.split('.')[0] for f in os.listdir(trans_path) if f.endswith('.json'))
    else:
        transcription_files = set()

    # 2. Load DB
    with open('shared/episodes_database.json', 'r') as f:
        data = json.load(f)

    # 3. Process Episodes 001-074
    report_data = []
    for ep in data['episodes']:
        num_str = str(ep.get('number', ''))
        if not num_str.isdigit():
            continue
        
        num = int(num_str)
        if not (1 <= num <= 74):
            continue

        url = ep.get('space_url', '')
        space_id = url.split('/')[-1].split('?')[0] if url else None
        
        has_mp3 = space_id in audio_files if space_id else False
        has_trans = space_id in transcription_files if space_id else False
        
        report_data.append({
            'num': num,
            'title': ep.get('title', 'N/A'),
            'id': space_id if space_id else 'N/A',
            'mp3': '✅' if has_mp3 else '❌',
            'trans': '✅' if has_trans else '❌'
        })

    # Sort by number descending
    report_data.sort(key=lambda x: x['num'], reverse=True)

    # Generate Markdown Table
    md_content = "# Episode Status Report (001-074)\n\n"
    md_content += "| # | Title | Space ID | MP3 | Transcript |\n"
    md_content += "|---|---|---|---|---|\n"
    for item in report_data:
        title = item['title']
        if len(title) > 40:
            title = title[:40] + "..."
        md_content += f"| {item['num']:03d} | {title} | `{item['id']}` | {item['mp3']} | {item['trans']} |\n"

    # Save to file
    output_path = 'shared/status_report_001_074.md'
    with open(output_path, 'w') as f:
        f.write(md_content)
    
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    generate_report()

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
            'description': ep.get('description', 'Sin descripción'),
            'id': space_id if space_id else 'N/A',
            'mp3': '✅' if has_mp3 else '❌',
            'trans': '✅' if has_trans else '❌',
            'guests': ep.get('guests', []),
            'host': ep.get('host', 'N/A'),
            'date': ep.get('date', 'N/A')
        })

    # Sort by number descending
    report_data.sort(key=lambda x: x['num'], reverse=True)

    # Generate Markdown Report with Details
    md_content = "# Episode Status Report (001-074)\n\n"
    md_content += f"**Total Episodes:** {len(report_data)}\n\n"
    md_content += "---\n\n"
    
    for item in report_data:
        md_content += f"## Episodio #{item['num']:03d}: {item['title']}\n\n"
        md_content += f"**Fecha:** {item['date']}\n\n"
        md_content += f"**Host:** {item['host']}\n\n"
        
        if item['guests']:
            guests_str = ', '.join(item['guests'])
            md_content += f"**Invitados:** {guests_str}\n\n"
        
        md_content += f"**Space ID:** `{item['id']}`\n\n"
        md_content += f"**Estado:**\n"
        md_content += f"- Audio MP3: {item['mp3']}\n"
        md_content += f"- Transcripción: {item['trans']}\n\n"
        
        md_content += f"**Descripción:**\n\n"
        md_content += f"{item['description']}\n\n"
        md_content += "---\n\n"

    # Save to file
    output_path = 'shared/status_report_001_074.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    generate_report()

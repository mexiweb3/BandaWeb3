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

    # 3. Process Co-Hosted Episodes
    report_data = []
    for ep in data['episodes']:
        if ep.get('type') != 'co-hosted':
            continue

        url = ep.get('space_url', '')
        space_id = url.split('/')[-1].split('?')[0] if url else None
        
        has_mp3 = space_id in audio_files if space_id else False
        has_trans = space_id in transcription_files if space_id else False
        
        # Use date as the primary identifier/sorter since co-hosted might not have numbers
        date = ep.get('date', 'N/A')
        
        report_data.append({
            'date': date,
            'title': ep.get('title', 'N/A'),
            'description': ep.get('description', 'Sin descripción'),
            'id': space_id if space_id else 'N/A',
            'mp3': '✅' if has_mp3 else '❌',
            'trans': '✅' if has_trans else '❌',
            'guests': ep.get('guests', []),
            'host': ep.get('host', 'N/A'),
            'duration': ep.get('duration', 'N/A'),
            'listeners': ep.get('listeners', 'N/A'),
            'space_url': url,
            'topics': ep.get('topics', [])
        })

    # Sort by date descending
    report_data.sort(key=lambda x: x['date'], reverse=True)

    # Generate Markdown Report with Details
    md_content = "# Co-Hosted Episodes Status Report\n\n"
    md_content += f"**Total Episodes:** {len(report_data)}\n\n"
    md_content += "---\n\n"
    
    for i, item in enumerate(report_data, 1):
        md_content += f"## {i}. {item['title']}\n\n"
        md_content += f"**Fecha:** {item['date']}\n\n"
        md_content += f"**Host:** {item['host']}\n\n"
        
        if item['guests']:
            guests_str = ', '.join(item['guests'])
            md_content += f"**Invitados:** {guests_str}\n\n"
        
        md_content += f"**Space ID:** `{item['id']}`\n\n"
        
        if item['space_url']:
            md_content += f"**URL:** [Link]({item['space_url']})\n\n"

        md_content += f"**Duración:** {item['duration']} | **Oyentes:** {item['listeners']}\n\n"

        if item['topics']:
            topics_str = ', '.join(item['topics'])
            md_content += f"**Temas:** {topics_str}\n\n"

        md_content += f"**Estado:**\n"
        md_content += f"- Audio MP3: {item['mp3']}\n"
        md_content += f"- Transcripción: {item['trans']}\n\n"
        
        md_content += f"**Descripción:**\n\n"
        md_content += f"{item['description']}\n\n"
        md_content += "---\n\n"

    # Save to file
    output_path = 'shared/status_report_cohosted.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Report generated at {output_path}")

if __name__ == "__main__":
    generate_report()

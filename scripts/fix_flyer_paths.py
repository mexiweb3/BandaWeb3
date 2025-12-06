#!/usr/bin/env python3
import json
import os
import glob

# Read the database
with open('data/episodes_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get all flyer files
flyer_files = glob.glob('website/static/images/flyer_*.*')
flyer_map = {}

# Create a map of episode number to actual file
for filepath in flyer_files:
    filename = os.path.basename(filepath)
    # Extract episode number from filename (e.g., flyer_034.png -> 034)
    parts = filename.replace('flyer_', '').rsplit('.', 1)
    if len(parts) == 2:
        episode_num = parts[0]
        ext = parts[1]
        # Store the file with extension
        if episode_num not in flyer_map:
            flyer_map[episode_num] = []
        flyer_map[episode_num].append(f'../static/images/{filename}')

print(f"Found {len(flyer_files)} flyer files")
print(f"Mapped to {len(flyer_map)} episode numbers")

# Update episodes
updated_count = 0
for episode in data['episodes']:
    episode_num = episode['number']
    
    # Check if we have a flyer for this episode
    if episode_num in flyer_map:
        old_urls = episode.get('flyer_urls', [])
        new_urls = flyer_map[episode_num]
        
        if old_urls != new_urls:
            episode['flyer_urls'] = new_urls
            updated_count += 1
            print(f"Updated episode {episode_num}: {new_urls}")

# Write back
with open('data/episodes_database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"\n✅ Updated {updated_count} episodes with correct flyer paths")

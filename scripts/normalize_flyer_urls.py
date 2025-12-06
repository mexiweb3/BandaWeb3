#!/usr/bin/env python3
import json

# Read the database
with open('data/episodes_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Normalize all flyer_urls to simple format
for episode in data['episodes']:
    if 'flyer_urls' in episode and episode['flyer_urls']:
        normalized_urls = []
        for url in episode['flyer_urls']:
            # Extract just the filename
            if 'flyer_' in url:
                filename = url.split('/')[-1]  # Get last part after /
                normalized_urls.append(f'/flyers/{filename}')
            else:
                normalized_urls.append(url)
        episode['flyer_urls'] = normalized_urls
        if normalized_urls:
            print(f"Episode {episode['number']}: {normalized_urls[0]}")

# Write back
with open('data/episodes_database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"\nNormalized flyer URLs for all episodes")

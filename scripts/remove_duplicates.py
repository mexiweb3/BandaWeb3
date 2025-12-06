#!/usr/bin/env python3
import json

# Read the database
with open('data/episodes_database.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Track seen episode numbers
seen = set()
unique_episodes = []

# Keep only first occurrence of each episode number
for episode in data['episodes']:
    episode_num = episode['number']
    if episode_num not in seen:
        seen.add(episode_num)
        unique_episodes.append(episode)
    else:
        print(f"Removing duplicate: {episode_num} - {episode.get('title', 'No title')}")

# Update the data
data['episodes'] = unique_episodes
data['metadata']['total_episodes'] = len(unique_episodes)

# Write back
with open('data/episodes_database.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"\nTotal episodes after deduplication: {len(unique_episodes)}")
print(f"Removed {len(data['episodes']) - len(unique_episodes)} duplicates")

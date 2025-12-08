import json
from pathlib import Path
import re

SHARED_DIR = Path('shared')
EPISODES_DB_PATH = SHARED_DIR / 'episodes_database.json'

def parse_duration_to_minutes(duration_str):
    if not duration_str:
        return 0
    
    # Handle HH:MM:SS or MM:SS
    parts = duration_str.split(':')
    if len(parts) == 3: # HH:MM:SS
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        return hours * 60 + minutes + (seconds / 60)
    elif len(parts) == 2: # MM:SS
        minutes = int(parts[0])
        seconds = int(parts[1])
        return minutes + (seconds / 60)
    else:
        return 0

def update_stats():
    if not EPISODES_DB_PATH.exists():
        print("Error: Episodes database not found.")
        return

    with open(EPISODES_DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    episodes = data.get('episodes', [])
    
    total_episodes = len(episodes)
    total_duration_minutes = 0
    total_listeners = 0
    listeners_count = 0 # Count of episodes that actually have listener data
    
    type_counts = {}

    for ep in episodes:
        # Duration
        dur_str = ep.get('duration', '')
        total_duration_minutes += parse_duration_to_minutes(dur_str)

        # Listeners
        listeners = ep.get('listeners')
        if listeners is not None:
             # Ensure it's a number
             try:
                 l_val = int(listeners)
                 total_listeners += l_val
                 listeners_count += 1
             except (ValueError, TypeError):
                 pass

        # Type breakdown
        ep_type = ep.get('type', 'unknown')
        type_counts[ep_type] = type_counts.get(ep_type, 0) + 1

    # Calculate averages
    avg_duration_minutes = total_duration_minutes / total_episodes if total_episodes > 0 else 0
    avg_listeners = total_listeners / listeners_count if listeners_count > 0 else 0

    stats = {
        "total_episodes": total_episodes,
        "total_duration_hours": round(total_duration_minutes / 60, 2),
        "average_duration_minutes": round(avg_duration_minutes, 1),
        "total_listeners": total_listeners,
        "average_listeners": round(avg_listeners, 1),
        "episodes_with_listener_data": listeners_count,
        "breakdown_by_type": type_counts,
        "last_updated": "2025-12-07" # In a real automated system this would be dynamic, but for now fixed or datetime.now()
    }

    # Add timestamp
    from datetime import datetime
    stats["last_updated"] = datetime.now().isoformat()

    data['stats'] = stats

    with open(EPISODES_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Episodes stats updated.")

    # Update Spoken Database
    SPOKEN_DB_PATH = SHARED_DIR / 'spoken_database.json'
    if SPOKEN_DB_PATH.exists():
        with open(SPOKEN_DB_PATH, 'r', encoding='utf-8') as f:
            spoken_data = json.load(f)
        
        spoken_eps = spoken_data.get('episodes', [])
        
        s_total = len(spoken_eps)
        s_duration = 0
        s_listeners = 0
        s_listeners_count = 0
        
        for ep in spoken_eps:
            s_duration += parse_duration_to_minutes(ep.get('duration', ''))
            
            l = ep.get('listeners')
            if l is not None:
                try:
                    lv = int(l)
                    s_listeners += lv
                    s_listeners_count += 1
                except:
                    pass
        
        s_avg_dur = s_duration / s_total if s_total > 0 else 0
        s_avg_lis = s_listeners / s_listeners_count if s_listeners_count > 0 else 0
        
        spoken_stats = {
            "total_episodes": s_total,
            "total_duration_hours": round(s_duration / 60, 2),
            "average_duration_minutes": round(s_avg_dur, 1),
            "total_listeners": s_listeners,
            "average_listeners": round(s_avg_lis, 1),
            "episodes_with_listener_data": s_listeners_count,
            "last_updated": datetime.now().isoformat()
        }
        
        spoken_data['stats'] = spoken_stats
        
        with open(SPOKEN_DB_PATH, 'w', encoding='utf-8') as f:
            json.dump(spoken_data, f, indent=2, ensure_ascii=False)
            
        print("Spoken stats updated.")
        print(json.dumps(spoken_stats, indent=2))
    else:
        print("Spoken database not found, skipping.")

if __name__ == "__main__":
    update_stats()

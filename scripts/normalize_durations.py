import json
import re
from datetime import timedelta
import os

def parse_duration_to_seconds(duration_str):
    if not duration_str:
        return 0
    
    duration_str = str(duration_str).lower().strip()
    
    if ':' in duration_str:
        parts = duration_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(float(s))
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + int(float(s))
            
    h = 0
    m = 0
    s = 0
    
    match_h = re.search(r'(\d+)\s*(?:hour|hours|h)', duration_str)
    if match_h:
        h = int(match_h.group(1))
        
    match_m = re.search(r'(\d+)\s*(?:minute|minutes|min|m)(?!s)', duration_str)
    if not match_m:
         match_m = re.search(r'(\d+)\s*m\b', duration_str)
         
    if match_m:
        m = int(match_m.group(1))
        
    match_s = re.search(r'(\d+)\s*(?:second|seconds|sec|s)\b', duration_str)
    if match_s:
        s = int(match_s.group(1))
        
    if h or m or s:
        return h * 3600 + m * 60 + s
        
    if duration_str.isdigit():
        return int(duration_str) * 60 
        
    return 0

def format_duration_hhmmss(duration_str):
    seconds = parse_duration_to_seconds(duration_str)
    if seconds == 0 and str(duration_str) != "0":
        return duration_str
        
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

def normalize_database():
    base_dir = "."
    input_file = os.path.join(base_dir, "shared/episodes_database.json")
    
    print(f"Loading {input_file}...")
    with open(input_file, "r") as f:
        data = json.load(f)
        
    episodes = data.get("episodes", [])
    modified_count = 0
    
    for ep in episodes:
        raw_duration = ep.get("duration", "")
        # Check if already in correct format
        # If HH:MM:SS, leave it to ensure we don't zero it if logic fails
        # But we want to standardize e.g. 1:2:3 to 01:02:03
        
        normalized = format_duration_hhmmss(raw_duration)
        if normalized != raw_duration:
            ep["duration"] = normalized
            modified_count += 1
            
    print(f"Normalized {modified_count} episode durations.")
    
    with open(input_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved updated {input_file}.")

if __name__ == "__main__":
    normalize_database()

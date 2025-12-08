import openpyxl
import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

def format_seconds(seconds):
    return str(timedelta(seconds=seconds))

def parse_duration_to_seconds(duration_str):
    if not duration_str:
        return 0
    
    duration_str = duration_str.lower().strip()
    
    # Check for HH:MM:SS or MM:SS
    if ':' in duration_str:
        parts = duration_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(float(s))
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + int(float(s))
            
    # "1 hours, 2 minutes, 3 seconds"
    h = 0
    m = 0
    s = 0
    
    match_h = re.search(r'(\d+)\s*(?:hour|hours|h)', duration_str)
    if match_h:
        h = int(match_h.group(1))
        
    match_m = re.search(r'(\d+)\s*(?:minute|minutes|min|m)(?!s)', duration_str) # negative lookahead for ms? simplier: just look for m or min
    # Actually 'm' can match 'minutes' if we search specifically
    if not match_m:
         match_m = re.search(r'(\d+)\s*m\b', duration_str)
         
    if match_m:
        m = int(match_m.group(1))
        
    match_s = re.search(r'(\d+)\s*(?:second|seconds|sec|s)\b', duration_str)
    if match_s:
        s = int(match_s.group(1))
        
    if h or m or s:
        return h * 3600 + m * 60 + s
        
    # Fallback: simple integer treated as minutes? or seconds?
    # Usually safer to return 0 if unknown
    if duration_str.isdigit():
        return int(duration_str) * 60 # Assume minutes if just a number? Or ignore.
        
    return 0

def format_duration_hhmmss(duration_str):
    seconds = parse_duration_to_seconds(duration_str)
    if seconds == 0 and duration_str != "0":
        # Check if it was already 00:00:00 or similar?
        return duration_str
        
    # Format HH:MM:SS
    # timedelta string is usually H:MM:SS or D days, H:MM:SS
    td = timedelta(seconds=seconds)
    s = str(td)
    if len(s.split(':')) == 2: # 0:00:00
        return "0" + s if len(s) == 7 else s # 0:05:00 -> 00:05:00
        
    # If standard output, it might look like "1 day, 2:00:00". We just want HH:MM:SS total hours
    # Construct manually
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:02}"

def parse_host_from_link(hyperlink_target):
    if not hyperlink_target:
        return ""
    target = hyperlink_target.rstrip('/')
    handle = target.split('/')[-1]
    handle = handle.split('?')[0]
    if handle:
        return f"@{handle}"
    return ""

def parse_details(cell_value):
    if not cell_value:
        return "", "", 0, ""
    
    text = str(cell_value)
    
    parts = text.split(" - Ended: ")
    if len(parts) == 1:
        parts = text.split(" Ended: ")
        
    title = parts[0].strip()
    
    date_str = ""
    speakers = 0
    duration = ""
    
    if len(parts) > 1:
        remainder = parts[1]
        meta_parts = remainder.split(" - ")
        
        date_part = meta_parts[0].strip()
        try:
            dt = datetime.strptime(date_part, "%b %d %Y")
            date_str = dt.strftime("%Y-%m-%d")
        except:
             try:
                 dt = datetime.strptime(date_part, "%b %d, %Y")
                 date_str = dt.strftime("%Y-%m-%d")
             except:
                date_str = date_part

        for part in meta_parts[1:]:
            if part.startswith("Speakers: "):
                try:
                    speakers = int(part.replace("Speakers: ", "").strip())
                except:
                    pass
            elif part.startswith("Duration: "):
                raw_duration = part.replace("Duration: ", "").strip()
                duration = format_duration_hhmmss(raw_duration)
                
    return title, date_str, speakers, duration

def extract_urls(cell_b_hyperlink, cell_e_hyperlink):
    spacesdashboard_url = ""
    space_url = ""
    
    if cell_b_hyperlink:
        spacesdashboard_url = cell_b_hyperlink.target
        
    if cell_e_hyperlink:
        space_url = cell_e_hyperlink.target
        
    space_id = ""
    if spacesdashboard_url:
        match = re.search(r'space/([a-zA-Z0-9]{13})', spacesdashboard_url)
        if match:
            space_id = match.group(1)
            
    if not space_id and space_url:
        match = re.search(r'spaces/([a-zA-Z0-9]{13})', space_url)
        if match:
             space_id = match.group(1)

    if space_id:
        if not space_url:
            space_url = f"https://x.com/i/spaces/{space_id}"
            
    return space_url, spacesdashboard_url

def ingest_spoken():
    base_dir = "."
    input_file = os.path.join(base_dir, "shared/inputs/Spoken - Spaces Dashboard.xlsx")
    output_file = os.path.join(base_dir, "shared/spoken_database.json")

    print(f"Loading {input_file}...")
    wb = openpyxl.load_workbook(input_file)
    ws = wb.active

    episodes = []
    
    for row in ws.iter_rows(min_row=4, values_only=False):
        cell_host = row[0]
        cell_details = row[1]
        cell_listeners = row[2]
        cell_link = row[4]
        
        if not cell_details or not cell_details.value:
            continue

        host = ""
        if cell_host.hyperlink:
            host = parse_host_from_link(cell_host.hyperlink.target)
        else:
            if cell_host.value:
                 lines = str(cell_host.value).split('\n')
                 for line in lines:
                    if line.strip().startswith('@'):
                        host = line.strip()
                        break
                 if not host:
                     host = lines[0].strip()

        title, date, speakers, duration = parse_details(cell_details.value)
        
        listeners = 0
        if cell_listeners.value:
            try:
                listeners = int(cell_listeners.value)
            except:
                pass
        
        space_url, spacesdashboard_url = extract_urls(cell_details.hyperlink, cell_link.hyperlink)
        
        ep = {
            "type": "Spoken",
            "title": title,
            "host": host,
            "listeners": listeners,
            "date": date,
            "speakers": speakers,
            "duration": duration,
            "space_url": space_url,
            "spacesdashboard_url": spacesdashboard_url
        }
        
        episodes.append(ep)

    episodes.sort(key=lambda x: x.get("date", ""), reverse=True)

    date_groups = defaultdict(list)
    for ep in episodes:
        d = ep.get("date", "")
        if d:
             date_groups[d].append(ep)
    
    date_counters = defaultdict(int) 
    
    final_episodes = []
    
    for ep in episodes:
        d = ep.get("date", "")
        if not d:
            ep["number"] = "00000000" 
            final_episodes.append(ep)
            continue
            
        date_str_clean = d.replace("-", "")
        
        total_in_day = len(date_groups[d])
        
        date_counters[d] += 1
        current_idx = date_counters[d]
        
        if total_in_day > 1:
            ep["number"] = f"{date_str_clean}.{current_idx}"
        else:
            ep["number"] = date_str_clean
            
        final_episodes.append(ep)

    data = {
        "description": "Database from Spoken - Spaces Dashboard.xlsx",
        "generated_at": datetime.now().isoformat(),
        "count": len(final_episodes),
        "episodes": final_episodes
    }

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully generated {output_file} with {len(final_episodes)} episodes.")

if __name__ == "__main__":
    ingest_spoken()

#!/usr/bin/env python3
"""
Update episodes with number between 0 and 74 to have is_numbered=true
"""
import json

def update_numbered_range():
    path = 'shared/episodes_database.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    episodes = data.get('episodes', [])
    count = 0
    
    for ep in episodes:
        # Get number string
        num_str = str(ep.get('number', ''))
        
        # Try to convert to int
        try:
            # Handle cases like "001" or "1"
            if not num_str.isdigit():
                continue
                
            num_val = int(num_str)
            
            # Check range 0 to 74
            if 0 <= num_val <= 74:
                # Update fields
                if not ep.get('is_numbered'):
                    ep['is_numbered'] = True
                    ep['type'] = 'hosted'  # Ensure it is hosted type
                    if not ep.get('host'):
                        ep['host'] = 'BandaWeb3' # Default host if missing
                        
                    print(f"Updated: [{num_str}] {ep.get('title')}")
                    count += 1
                    
        except ValueError:
            continue
            
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"\nSuccessfully updated {count} new numbered episodes.")

if __name__ == '__main__':
    update_numbered_range()

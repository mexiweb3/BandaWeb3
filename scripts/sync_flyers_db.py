import json
import os
import re
import argparse

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'shared', 'episodes_database.json')
FLYERS_DIR = os.path.join(BASE_DIR, 'shared', 'flyers')

def sync_flyers(commit=False):
    print(f"Loading database from {DB_PATH}")
    with open(DB_PATH, 'r') as f:
        data = json.load(f)

    episodes = data.get('episodes', [])
    print(f"Found {len(episodes)} episodes.")

    # Get all files in flyers dir
    flyer_files = set(f for f in os.listdir(FLYERS_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png')))
    print(f"Found {len(flyer_files)} image files in {FLYERS_DIR}")

    updated_count = 0
    warnings = []

    # Map existing files to potential episode numbers
    # Expectation: flyer_044.jpg -> episode "044"
    # Also handle flyer_044_2.jpg -> episode "044"
    file_map = {}
    for filename in flyer_files:
        match = re.search(r'flyer_(\d+)', filename)
        if match:
            ep_num = match.group(1)
            if ep_num not in file_map:
                file_map[ep_num] = []
            file_map[ep_num].append(filename)
        else:
            warnings.append(f"Orphan file (no number detected): {filename}")

    # Process episodes
    for ep in episodes:
        ep_num = ep.get('number')
        if not ep_num:
            continue
        
        # Normalize to string just in case
        ep_num = str(ep_num)

        current_flyers = set(ep.get('flyer_urls', []))
        
        # Find matches on disk
        matches = set(file_map.get(ep_num, []))

        # Check for missing files (in DB but not on disk)
        missing_on_disk = current_flyers - flyer_files
        for missing in missing_on_disk:
            print(f"[WARNING] Episode {ep_num} references {missing} which DOES NOT EXIST on disk.")
            # We don't remove them automatically unless requested, but here we will prioritize disk truth if we are syncing
            # For now, let's keep them but warn, OR if we want to be strict, we rebuild the list from disk matches only.
            # Decision: The goal is to update info if missing. Let's merge found files.
        
        # Detect new files (on disk but not in DB)
        new_files = matches - current_flyers
        
        if new_files:
            print(f"[UPDATE] Episode {ep_num}: Found new matches on disk: {new_files}")
            # Merge and sort
            all_flyers = list(current_flyers.union(matches))
            # Filter out ones that definitely don't exist?
            # Let's trust disk. If it's on disk, it goes in. If it was in DB but not on disk... let's keep it but maybe it's a broken link.
            # Actually, to be clean, let's rebuild the list based on what is actually on disk IF there are matches on disk.
            # If no matches on disk, maybe we leave it alone (could be external URL?). But these look like filenames.
            
            # Rebuilding list from matches ensures no broken local links
            final_flyers = sorted(list(matches))
            if set(final_flyers) != set(ep.get('flyer_urls', [])):
                ep['flyer_urls'] = final_flyers
                updated_count += 1
        
        # Also check if keys are just missing
        elif not current_flyers and matches:
             print(f"[UPDATE] Episode {ep_num}: Had no flyers, adding: {matches}")
             ep['flyer_urls'] = sorted(list(matches))
             updated_count += 1

    # Check for totally unused files (Orphans that didn't map to an existing episode)
    episode_numbers = set(str(e.get('number')) for e in episodes)
    for ep_num, files in file_map.items():
        if ep_num not in episode_numbers:
             warnings.append(f"Files found for Episode {ep_num} but episode entry DOES NOT EXIST in DB: {files}")

    for w in warnings:
        print(f"[ALERT] {w}")

    if updated_count > 0:
        print(f"Total episodes to update: {updated_count}")
        if commit:
            print("Saving changes to database...")
            with open(DB_PATH, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Done.")
        else:
            print("Dry run complete. Use --commit to save changes.")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", action="store_true", help="Write changes to JSON file")
    args = parser.parse_args()
    sync_flyers(commit=args.commit)

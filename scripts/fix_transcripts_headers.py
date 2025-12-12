import os
import json
from pathlib import Path
from transcribe_deepgram import load_episode_metadata, format_episode_header

TRANSCRIPT_DIR = Path("shared/transcriptions")
HEADER_SIGNATURE = "INFORMACIÓN DEL EPISODIO"

def main():
    if not TRANSCRIPT_DIR.exists():
        print("Transcript directory not found.")
        return

    txt_files = list(TRANSCRIPT_DIR.glob("*.txt"))
    fixed_count = 0

    print(f"Scanning {len(txt_files)} transcript files for missing headers...")

    for txt_file in txt_files:
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            if HEADER_SIGNATURE in content:
                continue

            print(f"Fixing {txt_file.name}...")
            
            # Extract space_id from filename (remove .txt)
            space_id = txt_file.stem
            
            # Load metadata using the FIXED function from transcribe_deepgram
            episode = load_episode_metadata(space_id)
            
            if not episode:
                print(f"  ⚠️  Metadata not found for {space_id}")
                continue

            header = format_episode_header(episode)
            if not header:
                print(f"  ⚠️  Could not generate header for {space_id}")
                continue

            # Prepend header
            new_content = header + "\n" + content
            
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print(f"  ✅ Fixed header for {space_id}")
            fixed_count += 1

        except Exception as e:
            print(f"Error processing {txt_file.name}: {e}")

    print(f"\nSummary: Fixed {fixed_count} files.")

if __name__ == "__main__":
    main()

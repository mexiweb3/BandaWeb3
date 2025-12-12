import os
from pathlib import Path

TRANSCRIPT_DIR = Path("shared/transcriptions")
HEADER_SIGNATURE = "INFORMACIÓN DEL EPISODIO"

def main():
    if not TRANSCRIPT_DIR.exists():
        print("Transcript directory not found.")
        return

    txt_files = list(TRANSCRIPT_DIR.glob("*.txt"))
    missing_header_files = []

    print(f"Scanning {len(txt_files)} transcript files...")

    for txt_file in txt_files:
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read(500) # Read first 500 chars
                if HEADER_SIGNATURE not in content:
                    missing_header_files.append(txt_file.name)
        except Exception as e:
            print(f"Error reading {txt_file.name}: {e}")

    print(f"\nFound {len(missing_header_files)} files missing metadata header:")
    for filename in sorted(missing_header_files):
        print(f"- {filename}")

if __name__ == "__main__":
    main()

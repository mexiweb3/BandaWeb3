#!/usr/bin/env python3
"""
BandaWeb3 Batch Episode Downloader
Downloads multiple episodes using TwitterSpaceGPT.

Usage:
    python3 batch_download_episodes.py --episodes 074,073,072
    python3 batch_download_episodes.py --all --pending
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import auto_download_agent
try:
    from auto_download_agent import AutoDownloadAgent
except ImportError:
    print(f"{Fore.RED}❌ auto_download_agent.py not found")
    sys.exit(1)

class BatchEpisodeDownloader:
    """Batch download multiple episodes."""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "data" / "episodes_database.json"
        self.output_base = Path(__file__).parent.parent.parent
    
    def load_database(self) -> Dict:
        """Load episodes database."""
        if not self.db_path.exists():
            print(f"{Fore.RED}❌ Database not found: {self.db_path}")
            sys.exit(1)
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_database(self, db: Dict):
        """Save episodes database."""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
    
    def get_episodes_to_download(self, episode_nums: List[str] = None, pending_only: bool = False) -> List[Dict]:
        """Get list of episodes to download."""
        db = self.load_database()
        episodes = db.get("episodes", [])
        
        to_download = []
        
        for ep in episodes:
            # Filter by episode numbers if specified
            if episode_nums and ep["number"] not in episode_nums:
                continue
            
            # Filter by pending status if specified
            if pending_only and ep.get("audio_url") and os.path.exists(ep["audio_url"]):
                continue
            
            # Check if has Space URL
            if not ep.get("space_url"):
                print(f"{Fore.YELLOW}⚠️  Episode {ep['number']}: No Space URL, skipping")
                continue
            
            to_download.append(ep)
        
        return to_download
    
    def download_episode(self, episode: Dict) -> bool:
        """Download single episode using auto_download_agent."""
        episode_num = episode["number"]
        space_url = episode["space_url"]
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Downloading Episode {episode_num}: {episode['title']}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        try:
            # Use auto_download_agent
            agent = AutoDownloadAgent(
                space_url=space_url,
                episode_number=episode_num,
                process_after_download=False  # Don't process, just download
            )
            
            # Submit and wait for download
            success = agent.submit_and_monitor()
            
            if success:
                # Update database with audio path
                audio_path = agent.get_downloaded_file_path()
                if audio_path and os.path.exists(audio_path):
                    episode["audio_url"] = str(audio_path)
                    episode["status"] = "audio_downloaded"
                    print(f"{Fore.GREEN}✓ Episode {episode_num} downloaded successfully")
                    return True
            
            print(f"{Fore.RED}❌ Episode {episode_num} download failed")
            return False
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error downloading episode {episode_num}: {e}")
            return False
    
    def batch_download(self, episodes: List[Dict], delay_between: int = 60):
        """Download multiple episodes with delay between submissions."""
        total = len(episodes)
        successful = 0
        failed = 0
        
        print(f"\n{Fore.CYAN}Starting batch download of {total} episodes")
        print(f"{Fore.CYAN}Delay between submissions: {delay_between} seconds\n")
        
        db = self.load_database()
        
        for i, episode in enumerate(episodes, 1):
            print(f"\n{Fore.BLUE}[{i}/{total}] Processing Episode {episode['number']}")
            
            success = self.download_episode(episode)
            
            if success:
                successful += 1
                # Update database
                for j, ep in enumerate(db["episodes"]):
                    if ep["number"] == episode["number"]:
                        db["episodes"][j] = episode
                        break
                self.save_database(db)
            else:
                failed += 1
            
            # Delay before next (except for last one)
            if i < total:
                print(f"\n{Fore.YELLOW}⏳ Waiting {delay_between} seconds before next episode...")
                time.sleep(delay_between)
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Batch Download Summary")
        print(f"{Fore.CYAN}{'='*60}\n")
        print(f"{Fore.GREEN}✓ Successful: {successful}/{total}")
        print(f"{Fore.RED}✗ Failed: {failed}/{total}")
        print(f"\n{Fore.GREEN}✅ Batch download complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Batch download BandaWeb3 episodes"
    )
    parser.add_argument(
        "--episodes",
        help="Comma-separated episode numbers (e.g., 074,073,072)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all episodes"
    )
    parser.add_argument(
        "--pending",
        action="store_true",
        help="Only download episodes without audio"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=60,
        help="Delay between downloads in seconds (default: 60)"
    )
    
    args = parser.parse_args()
    
    downloader = BatchEpisodeDownloader()
    
    # Get episodes to download
    episode_nums = None
    if args.episodes:
        episode_nums = [num.strip() for num in args.episodes.split(",")]
    
    episodes = downloader.get_episodes_to_download(
        episode_nums=episode_nums,
        pending_only=args.pending
    )
    
    if not episodes:
        print(f"{Fore.YELLOW}⚠️  No episodes to download")
        sys.exit(0)
    
    # Confirm
    print(f"\n{Fore.CYAN}Episodes to download:")
    for ep in episodes:
        print(f"  - Episode {ep['number']}: {ep['title']}")
    
    confirm = input(f"\n{Fore.YELLOW}Proceed with download? (y/n): ")
    if confirm.lower() != 'y':
        print(f"{Fore.YELLOW}Cancelled")
        sys.exit(0)
    
    # Download
    downloader.batch_download(episodes, delay_between=args.delay)


if __name__ == "__main__":
    main()

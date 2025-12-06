#!/usr/bin/env python3
"""
BandaWeb3 Space Metadata Extractor
Extracts metadata from X Spaces and updates episodes database.

Usage:
    python3 extract_space_metadata.py <space_url> --episode 075
    python3 extract_space_metadata.py --batch episodes_list.txt
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import requests
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

class SpaceMetadataExtractor:
    """Extracts metadata from X Spaces."""
    
    def __init__(self):
        self.bearer_token = os.getenv("X_BEARER_TOKEN")
        
        if not self.bearer_token:
            print(f"{Fore.YELLOW}⚠️  X_BEARER_TOKEN not found")
            print(f"{Fore.YELLOW}Will use manual input mode")
        
        self.api_base = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        } if self.bearer_token else None
        
        # Database path
        self.db_path = Path(__file__).parent.parent / "data" / "episodes_database.json"
    
    def extract_space_id(self, space_url: str) -> Optional[str]:
        """Extract Space ID from URL."""
        # URL format: https://twitter.com/i/spaces/1BRJjZYXXXXXX
        if "/spaces/" in space_url:
            return space_url.split("/spaces/")[1].split("?")[0]
        return None
    
    def get_space_metadata(self, space_id: str) -> Optional[Dict]:
        """Get Space metadata from X API."""
        if not self.headers:
            print(f"{Fore.YELLOW}⚠️  No API access, using manual mode")
            return None
        
        try:
            url = f"{self.api_base}/spaces/{space_id}"
            params = {
                "space.fields": "title,created_at,started_at,ended_at,participant_count,speaker_ids,host_ids,scheduled_start,state",
                "expansions": "host_ids,speaker_ids",
                "user.fields": "name,username"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"{Fore.RED}❌ API Error: {response.status_code}")
                print(f"{Fore.RED}{response.text}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}")
            return None
    
    def manual_input_metadata(self, episode_num: str) -> Dict:
        """Manually input episode metadata."""
        print(f"\n{Fore.CYAN}Manual metadata input for Episode {episode_num}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        title = input("Title: ")
        date = input("Date (YYYY-MM-DD): ")
        guests = input("Guests (comma-separated): ").split(",")
        guests = [g.strip() for g in guests if g.strip()]
        duration = input("Duration (e.g., '90 min'): ")
        description = input("Description: ")
        topics = input("Topics (comma-separated): ").split(",")
        topics = [t.strip() for t in topics if t.strip()]
        
        return {
            "number": episode_num,
            "title": title,
            "date": date,
            "space_url": "",
            "audio_url": "",
            "flyer_url": "",
            "guests": guests,
            "duration": duration,
            "description": description,
            "topics": topics,
            "status": "pending",
            "transcript_available": False,
            "content_generated": False
        }
    
    def parse_space_data(self, space_data: Dict, episode_num: str) -> Dict:
        """Parse Space API response into episode format."""
        data = space_data.get("data", {})
        includes = space_data.get("includes", {})
        
        # Get title
        title = data.get("title", "")
        
        # Get date
        started_at = data.get("started_at") or data.get("scheduled_start")
        date = started_at.split("T")[0] if started_at else ""
        
        # Get speakers/hosts
        users = includes.get("users", [])
        guests = [user.get("name", user.get("username", "")) for user in users]
        
        # Calculate duration
        started = data.get("started_at")
        ended = data.get("ended_at")
        duration = "Unknown"
        
        if started and ended:
            start_time = datetime.fromisoformat(started.replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(ended.replace("Z", "+00:00"))
            duration_mins = int((end_time - start_time).total_seconds() / 60)
            duration = f"{duration_mins} min"
        
        return {
            "number": episode_num,
            "title": title,
            "date": date,
            "space_url": "",
            "audio_url": "",
            "flyer_url": "",
            "guests": guests,
            "duration": duration,
            "description": "",
            "topics": [],
            "status": "metadata_extracted",
            "transcript_available": False,
            "content_generated": False
        }
    
    def load_database(self) -> Dict:
        """Load episodes database."""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "metadata": {
                    "podcast_name": "BandaWeb3",
                    "last_updated": datetime.now().isoformat()
                },
                "episodes": [],
                "stats": {
                    "total_episodes": 0
                }
            }
    
    def save_database(self, db: Dict):
        """Save episodes database."""
        db["metadata"]["last_updated"] = datetime.now().isoformat()
        db["stats"]["total_episodes"] = len(db["episodes"])
        
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
        
        print(f"{Fore.GREEN}✓ Database updated: {self.db_path}")
    
    def add_episode(self, episode_data: Dict):
        """Add or update episode in database."""
        db = self.load_database()
        
        # Check if episode exists
        existing_index = None
        for i, ep in enumerate(db["episodes"]):
            if ep["number"] == episode_data["number"]:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing
            db["episodes"][existing_index] = episode_data
            print(f"{Fore.YELLOW}⚠️  Updated existing episode {episode_data['number']}")
        else:
            # Add new
            db["episodes"].append(episode_data)
            print(f"{Fore.GREEN}✓ Added new episode {episode_data['number']}")
        
        # Sort by episode number (descending)
        db["episodes"].sort(key=lambda x: x["number"], reverse=True)
        
        self.save_database(db)
    
    def extract_and_save(self, space_url: str, episode_num: str):
        """Extract metadata and save to database."""
        print(f"\n{Fore.CYAN}Extracting metadata for Episode {episode_num}")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        if space_url:
            space_id = self.extract_space_id(space_url)
            
            if not space_id:
                print(f"{Fore.RED}❌ Invalid Space URL")
                return
            
            print(f"{Fore.CYAN}Space ID: {space_id}")
            
            # Get metadata from API
            space_data = self.get_space_metadata(space_id)
            
            if space_data:
                episode_data = self.parse_space_data(space_data, episode_num)
                episode_data["space_url"] = space_url
                print(f"{Fore.GREEN}✓ Metadata extracted from API")
            else:
                print(f"{Fore.YELLOW}⚠️  Falling back to manual input")
                episode_data = self.manual_input_metadata(episode_num)
                episode_data["space_url"] = space_url
        else:
            # No URL, manual input
            episode_data = self.manual_input_metadata(episode_num)
        
        # Save to database
        self.add_episode(episode_data)
        
        # Display summary
        print(f"\n{Fore.GREEN}✅ Episode {episode_num} added to database")
        print(f"\n{Fore.CYAN}Summary:")
        print(f"  Title: {episode_data['title']}")
        print(f"  Date: {episode_data['date']}")
        print(f"  Guests: {', '.join(episode_data['guests'])}")
        print(f"  Duration: {episode_data['duration']}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract Space metadata and update episodes database"
    )
    parser.add_argument(
        "space_url",
        nargs="?",
        help="Space URL (optional if using --manual)"
    )
    parser.add_argument(
        "-e", "--episode",
        required=True,
        help="Episode number (e.g., 075)"
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Manual input mode (no API)"
    )
    
    args = parser.parse_args()
    
    extractor = SpaceMetadataExtractor()
    
    if args.manual or not args.space_url:
        episode_data = extractor.manual_input_metadata(args.episode)
        extractor.add_episode(episode_data)
    else:
        extractor.extract_and_save(args.space_url, args.episode)


if __name__ == "__main__":
    main()

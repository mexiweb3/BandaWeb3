#!/usr/bin/env python3
"""
BandaWeb3 Website Generator
Generates static website from episodes database.

Usage:
    python3 generate_website.py
    python3 generate_website.py --output ./custom_output
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List
from jinja2 import Environment, FileSystemLoader

# Initialize colorama
class Fore:
    CYAN = ""
    GREEN = ""
    RED = ""
    YELLOW = ""
class Style:
    RESET_ALL = ""

class WebsiteGenerator:
    """Generates static website for BandaWeb3 episodes."""
    
    def __init__(self, output_dir: str = None):
        self.base_dir = Path(__file__).parent.parent
        self.db_path = self.base_dir / "data" / "episodes_database.json"
        self.templates_dir = self.base_dir / "website" / "templates"
        self.static_dir = self.base_dir / "website" / "static"
        self.output_dir = Path(output_dir) if output_dir else self.base_dir / "website" / "output"
        
        # Setup Jinja2
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        self.env.filters['urlencode'] = lambda x: x.replace(' ', '%20')
    
    def load_database(self) -> Dict:
        """Load episodes database."""
        if not self.db_path.exists():
            print(f"{Fore.RED}❌ Database not found: {self.db_path}")
            sys.exit(1)
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def setup_output_directory(self):
        """Create output directory structure."""
        print(f"{Fore.CYAN}Setting up output directory...")
        
        # Create directories
        (self.output_dir / "episodes").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "static").mkdir(exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
        (self.output_dir / "flyers").mkdir(exist_ok=True)
        (self.output_dir / "transcripts").mkdir(exist_ok=True)
        
        # Copy static files
        if self.static_dir.exists():
            for file in self.static_dir.glob("*"):
                if file.is_file():
                    shutil.copy2(file, self.output_dir / "static" / file.name)
        
        print(f"{Fore.GREEN}✓ Output directory ready: {self.output_dir}")
    
    def copy_assets(self, episodes: List[Dict]):
        """Copy audio files and flyers to output directory."""
        print(f"\n{Fore.CYAN}Copying assets...")
        
        for episode in episodes:
            # Copy audio
            if episode.get("audio_url"):
                audio_path = Path(episode["audio_url"])
                if audio_path.exists():
                    dest = self.output_dir / "audio" / audio_path.name
                    shutil.copy2(audio_path, dest)
                    episode["audio_url"] = f"../audio/{audio_path.name}"
                    print(f"{Fore.GREEN}✓ Copied audio for episode {episode['number']}")
            
            # Copy flyer
            if episode.get("flyer_url") and os.path.exists(episode["flyer_url"]):
                flyer_path = Path(episode["flyer_url"])
                dest = self.output_dir / "flyers" / flyer_path.name
                shutil.copy2(flyer_path, dest)
                episode["flyer_url"] = f"../flyers/{flyer_path.name}"
                print(f"{Fore.GREEN}✓ Copied flyer for episode {episode['number']}")
    
    def generate_episode_page(self, episode: Dict, prev_episode: Dict = None, next_episode: Dict = None):
        """Generate individual episode page."""
        template = self.env.get_template("episode.html")
        
        # Create a copy to avoid modifying the original
        ep_copy = episode.copy()
        
        # Handle flyer_url(s) - use first from array if singular not present
        if not ep_copy.get("flyer_url") and ep_copy.get("flyer_urls") and len(ep_copy["flyer_urls"]) > 0:
            ep_copy["flyer_url"] = ep_copy["flyer_urls"][0]
        
        html = template.render(
            episode=ep_copy,
            prev_episode=prev_episode,
            next_episode=next_episode,
            page_url=f"https://bandaweb3.com/episodes/episode_{episode['number']}.html"
        )
        
        output_file = self.output_dir / "episodes" / f"episode_{episode['number']}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"{Fore.GREEN}✓ Generated page for episode {episode['number']}")
    
    
    def generate_index_page(self, episodes: List[Dict], stats: Dict):
        """Generate homepage with latest 6 episodes."""
        template = self.env.get_template("index.html")
        
        # Sort episodes by date (newest first) and take latest 6
        sorted_eps = sorted(episodes, key=lambda x: x.get('date', ''), reverse=True)
        latest_6 = sorted_eps[:6]
        
        # Calculate stats
        total_episodes = len(episodes)
        total_minutes = 0
        
        index_episodes = []
        for ep in latest_6:
            ep_copy = ep.copy()
            
            # Handle flyer_url(s) and path correction
            f_url = None
            if ep.get("flyer_urls") and len(ep["flyer_urls"]) > 0:
                f_url = ep["flyer_urls"][0]
            elif ep.get("flyer_url"):
                f_url = ep["flyer_url"]
            
            if f_url:
                if f_url.startswith("../"):
                    ep_copy["flyer_url"] = f_url[3:]
                else:
                    ep_copy["flyer_url"] = f_url
            
            index_episodes.append(ep_copy)

        # Calculate total hours from all episodes
        for ep in episodes:
            d_str = ep.get("duration", "0 min")
            matched = False
            if 'h' in d_str:
                parts = d_str.replace("m", "").split("h")
                try:
                    h = int(parts[0].strip()) if parts[0].strip() else 0
                    m = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0
                    total_minutes += h * 60 + m
                    matched = True
                except:
                    pass
            
            if not matched:
                try:
                    val = int(d_str.split()[0])
                    total_minutes += val
                except:
                    pass

        total_hours = total_minutes / 60
        
        html = template.render(
            latest_episodes=index_episodes,
            total_episodes=total_episodes,
            total_hours=int(total_hours)
        )
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"{Fore.GREEN}✓ Generated index page")
    
    def generate_hosted_page(self, episodes: List[Dict], stats: Dict):
        """Generate page with all hosted spaces (numeric IDs)."""
        template = self.env.get_template("hosted.html")
        
        # Filter hosted episodes (numeric IDs like 001, 072, etc.)
        hosted = [ep for ep in episodes if ep['number'].isdigit() or (ep['number'].isdigit() and len(ep['number']) <= 3)]
        
        # Sort by date (newest first)
        hosted_sorted = sorted(hosted, key=lambda x: x.get('date', ''), reverse=True)
        
        # Prepare episodes with correct paths
        hosted_episodes = []
        for ep in hosted_sorted:
            ep_copy = ep.copy()
            f_url = None
            if ep.get("flyer_urls") and len(ep["flyer_urls"]) > 0:
                f_url = ep["flyer_urls"][0]
            elif ep.get("flyer_url"):
                f_url = ep["flyer_url"]
            if f_url and f_url.startswith("../"):
                ep_copy["flyer_url"] = f_url[3:]
            elif f_url:
                ep_copy["flyer_url"] = f_url
            hosted_episodes.append(ep_copy)
        
        html = template.render(
            episodes=hosted_episodes,
            total_episodes=len(hosted_episodes),
            total_hours=stats.get('total_hours', 0)
        )
        
        output_file = self.output_dir / "hosted.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"{Fore.GREEN}✓ Generated hosted spaces page")
    
    def generate_cohosted_page(self, episodes: List[Dict], stats: Dict):
        """Generate page with all co-hosted spaces (date-based IDs)."""
        template = self.env.get_template("cohosted.html")
        
        # Filter co-hosted episodes (date-based IDs like 20230213)
        cohosted = [ep for ep in episodes if not ep['number'].isdigit() or len(ep['number']) > 3]
        
        # Sort by date (newest first)
        cohosted_sorted = sorted(cohosted, key=lambda x: x.get('date', ''), reverse=True)
        
        # Prepare episodes with correct paths
        cohosted_episodes = []
        for ep in cohosted_sorted:
            ep_copy = ep.copy()
            f_url = None
            if ep.get("flyer_urls") and len(ep["flyer_urls"]) > 0:
                f_url = ep["flyer_urls"][0]
            elif ep.get("flyer_url"):
                f_url = ep["flyer_url"]
            if f_url and f_url.startswith("../"):
                ep_copy["flyer_url"] = f_url[3:]
            elif f_url:
                ep_copy["flyer_url"] = f_url
            cohosted_episodes.append(ep_copy)
        
        html = template.render(
            episodes=cohosted_episodes,
            total_episodes=len(cohosted_episodes),
            total_hours=stats.get('total_hours', 0)
        )
        
        output_file = self.output_dir / "cohosted.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"{Fore.GREEN}✓ Generated co-hosted spaces page")
    
    def generate_rss_feed(self, episodes: List[Dict], metadata: Dict):
        """Generate RSS feed."""
        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{metadata.get('podcast_name', 'BandaWeb3')}</title>
    <description>{metadata.get('description', 'Podcast sobre Web3 y Blockchain')}</description>
    <link>{metadata.get('website', 'https://bandaweb3.com')}</link>
    <language>{metadata.get('language', 'es')}</language>
    <itunes:author>{metadata.get('host', 'BandaWeb3')}</itunes:author>
"""
        
        for episode in episodes[:10]:  # Last 10 episodes
            rss += f"""
    <item>
      <title>#{episode['number']} - {episode['title']}</title>
      <description>{episode.get('description', '')}</description>
      <pubDate>{episode.get('date', '')}</pubDate>
      <link>https://bandaweb3.com/episodes/episode_{episode['number']}.html</link>
      <guid>https://bandaweb3.com/episodes/episode_{episode['number']}.html</guid>
    </item>
"""
        
        rss += """
  </channel>
</rss>
"""
        
        output_file = self.output_dir / "rss.xml"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(rss)
        
        print(f"{Fore.GREEN}✓ Generated RSS feed")
    
    def generate(self):
        """Generate complete website."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}BandaWeb3 Website Generator")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Load database
        db = self.load_database()
        episodes = db.get("episodes", [])
        metadata = db.get("metadata", {})
        
        if not episodes:
            print(f"{Fore.YELLOW}⚠️  No episodes found in database")
            return
        
        print(f"{Fore.CYAN}Found {len(episodes)} episodes")
        
        # Setup output directory
        self.setup_output_directory()
        
        # Copy assets
        self.copy_assets(episodes)
        
        # Generate episode pages
        print(f"\n{Fore.CYAN}Generating episode pages...")
        for i, episode in enumerate(episodes):
            prev_ep = episodes[i + 1] if i + 1 < len(episodes) else None
            next_ep = episodes[i - 1] if i > 0 else None
            self.generate_episode_page(episode, prev_ep, next_ep)
        
        # Generate index page
        print(f"\n{Fore.CYAN}Generating index page...")
        self.generate_index_page(episodes, db.get("stats", {}))
        
        # Generate hosted page
        print(f"\n{Fore.CYAN}Generating hosted spaces page...")
        self.generate_hosted_page(episodes, db.get("stats", {}))
        
        # Generate co-hosted page
        print(f"\n{Fore.CYAN}Generating co-hosted spaces page...")
        self.generate_cohosted_page(episodes, db.get("stats", {}))
        
        # Generate RSS feed
        print(f"\n{Fore.CYAN}Generating RSS feed...")
        self.generate_rss_feed(episodes, metadata)
        
        # Summary
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}✅ Website generated successfully!")
        print(f"{Fore.CYAN}{'='*60}\n")
        print(f"{Fore.CYAN}Output directory: {self.output_dir}")
        print(f"{Fore.CYAN}Total pages: {len(episodes) + 1}")
        print(f"\n{Fore.YELLOW}To preview locally:")
        print(f"{Fore.YELLOW}  cd {self.output_dir}")
        print(f"{Fore.YELLOW}  python3 -m http.server 8000")
        print(f"{Fore.YELLOW}  Open http://localhost:8000\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate BandaWeb3 static website"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: website/output)"
    )
    
    args = parser.parse_args()
    
    generator = WebsiteGenerator(output_dir=args.output)
    generator.generate()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
BandaWeb3 Instagram Publisher
Publishes content to Instagram using the Instagram Graph API.

Usage:
    python3 publish_instagram.py <episode_dir> [options]
    
Examples:
    # Test connection
    python3 publish_instagram.py --test-connection
    
    # Publish single image
    python3 publish_instagram.py ../E075_* --type image --image path/to/image.jpg
    
    # Publish carousel
    python3 publish_instagram.py ../E075_* --type carousel --images 7
    
    # Schedule for later
    python3 publish_instagram.py ../E075_* --type image --schedule "2024-12-06 14:00"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import requests
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

class InstagramPublisher:
    """Publishes content to Instagram."""
    
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.business_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        
        if not self.access_token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN not found in environment variables")
        if not self.business_account_id:
            raise ValueError("INSTAGRAM_BUSINESS_ACCOUNT_ID not found in environment variables")
        
        self.api_base = "https://graph.facebook.com/v18.0"
    
    def test_connection(self) -> bool:
        """Test Instagram API connection."""
        try:
            print(f"{Fore.CYAN}Testing Instagram API connection...")
            
            # Get account info
            url = f"{self.api_base}/{self.business_account_id}"
            params = {
                "fields": "id,username,name",
                "access_token": self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                account_data = response.json()
                print(f"{Fore.GREEN}✓ Connected to Instagram API")
                print(f"{Fore.CYAN}Account: @{account_data.get('username', 'Unknown')}")
                print(f"{Fore.CYAN}Name: {account_data.get('name', 'Unknown')}")
                return True
            else:
                print(f"{Fore.RED}❌ Connection failed: {response.status_code}")
                print(f"{Fore.RED}Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error testing connection: {e}")
            return False
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        Upload image to Instagram's hosting.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Image URL or None if failed
        """
        # For Instagram Graph API, images must be publicly accessible URLs
        # This is a limitation - you need to host images somewhere first
        print(f"{Fore.YELLOW}⚠️  Instagram Graph API requires publicly accessible image URLs")
        print(f"{Fore.YELLOW}Please upload {image_path} to a public host (e.g., Imgur, Cloudinary)")
        print(f"{Fore.YELLOW}Or use Facebook's image upload endpoint")
        
        # TODO: Implement image upload to Facebook/Instagram
        # For now, return None and require manual URL input
        return None
    
    def create_media_container(self, image_url: str, caption: str) -> Optional[str]:
        """
        Create a media container for publishing.
        
        Args:
            image_url: Publicly accessible image URL
            caption: Post caption
        
        Returns:
            Container ID or None if failed
        """
        try:
            url = f"{self.api_base}/{self.business_account_id}/media"
            params = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
            
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                container_id = response.json().get("id")
                print(f"{Fore.GREEN}✓ Media container created: {container_id}")
                return container_id
            else:
                print(f"{Fore.RED}❌ Failed to create container: {response.status_code}")
                print(f"{Fore.RED}Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating container: {e}")
            return None
    
    def create_carousel_container(self, image_urls: List[str], caption: str) -> Optional[str]:
        """
        Create a carousel container for multiple images.
        
        Args:
            image_urls: List of publicly accessible image URLs
            caption: Post caption
        
        Returns:
            Container ID or None if failed
        """
        try:
            # First, create containers for each image
            children_ids = []
            
            for i, image_url in enumerate(image_urls, 1):
                print(f"{Fore.CYAN}Creating container for image {i}/{len(image_urls)}...")
                
                url = f"{self.api_base}/{self.business_account_id}/media"
                params = {
                    "image_url": image_url,
                    "is_carousel_item": True,
                    "access_token": self.access_token
                }
                
                response = requests.post(url, params=params)
                
                if response.status_code == 200:
                    child_id = response.json().get("id")
                    children_ids.append(child_id)
                    print(f"{Fore.GREEN}✓ Container {i} created: {child_id}")
                else:
                    print(f"{Fore.RED}❌ Failed to create container {i}")
                    return None
            
            # Create carousel container
            print(f"{Fore.CYAN}Creating carousel container...")
            
            url = f"{self.api_base}/{self.business_account_id}/media"
            params = {
                "media_type": "CAROUSEL",
                "children": ",".join(children_ids),
                "caption": caption,
                "access_token": self.access_token
            }
            
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                carousel_id = response.json().get("id")
                print(f"{Fore.GREEN}✓ Carousel container created: {carousel_id}")
                return carousel_id
            else:
                print(f"{Fore.RED}❌ Failed to create carousel: {response.status_code}")
                print(f"{Fore.RED}Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating carousel: {e}")
            return None
    
    def publish_container(self, container_id: str) -> Dict:
        """
        Publish a media container.
        
        Args:
            container_id: Container ID from create_media_container
        
        Returns:
            Dict with post URL and metadata
        """
        try:
            print(f"{Fore.CYAN}Publishing container {container_id}...")
            
            url = f"{self.api_base}/{self.business_account_id}/media_publish"
            params = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                media_id = response.json().get("id")
                print(f"{Fore.GREEN}✓ Post published successfully!")
                print(f"{Fore.CYAN}Media ID: {media_id}")
                
                return {
                    "success": True,
                    "media_id": media_id,
                    "url": f"https://www.instagram.com/p/{media_id}/",
                    "published_at": datetime.now().isoformat()
                }
            else:
                print(f"{Fore.RED}❌ Failed to publish: {response.status_code}")
                print(f"{Fore.RED}Response: {response.text}")
                return {
                    "success": False,
                    "error": response.text
                }
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error publishing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def publish_image(self, image_url: str, caption: str) -> Dict:
        """
        Publish a single image to Instagram.
        
        Args:
            image_url: Publicly accessible image URL
            caption: Post caption
        
        Returns:
            Dict with post URL and metadata
        """
        # Create container
        container_id = self.create_media_container(image_url, caption)
        
        if not container_id:
            return {"success": False, "error": "Failed to create media container"}
        
        # Publish
        return self.publish_container(container_id)
    
    def publish_carousel(self, image_urls: List[str], caption: str) -> Dict:
        """
        Publish a carousel to Instagram.
        
        Args:
            image_urls: List of publicly accessible image URLs
            caption: Post caption
        
        Returns:
            Dict with post URL and metadata
        """
        # Validate
        if len(image_urls) < 2:
            return {"success": False, "error": "Carousel requires at least 2 images"}
        if len(image_urls) > 10:
            return {"success": False, "error": "Carousel supports max 10 images"}
        
        # Create carousel container
        container_id = self.create_carousel_container(image_urls, caption)
        
        if not container_id:
            return {"success": False, "error": "Failed to create carousel container"}
        
        # Publish
        return self.publish_container(container_id)
    
    def schedule_post(self, post_data: Dict, schedule_time: str) -> Dict:
        """
        Schedule a post for later.
        
        Note: Instagram Graph API doesn't support native scheduling.
        This method saves the post data for later publishing via cron/n8n.
        
        Args:
            post_data: Post data (image_url, caption, type)
            schedule_time: Time to publish (format: "YYYY-MM-DD HH:MM")
        
        Returns:
            Dict with schedule info
        """
        try:
            # Parse schedule time
            scheduled_dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
            
            # Create scheduled posts directory
            schedule_dir = Path(__file__).parent.parent / "scheduled_posts"
            schedule_dir.mkdir(exist_ok=True)
            
            # Save post data
            scheduled_post = {
                "platform": "instagram",
                "post_data": post_data,
                "scheduled_time": scheduled_dt.isoformat(),
                "created_at": datetime.now().isoformat(),
                "status": "scheduled"
            }
            
            filename = f"instagram_{scheduled_dt.strftime('%Y%m%d_%H%M')}.json"
            filepath = schedule_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scheduled_post, f, indent=2, ensure_ascii=False)
            
            print(f"{Fore.GREEN}✓ Post scheduled for {schedule_time}")
            print(f"{Fore.CYAN}Saved to: {filepath}")
            print(f"{Fore.YELLOW}⚠️  Note: You need to set up a cron job or n8n workflow to publish scheduled posts")
            
            return {
                "success": True,
                "scheduled_time": scheduled_dt.isoformat(),
                "file": str(filepath)
            }
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error scheduling post: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    parser = argparse.ArgumentParser(
        description="Publish content to Instagram"
    )
    parser.add_argument(
        "episode_dir",
        nargs="?",
        help="Path to episode directory"
    )
    parser.add_argument(
        "-t", "--type",
        choices=["image", "carousel"],
        default="image",
        help="Post type (default: image)"
    )
    parser.add_argument(
        "--image",
        help="Image URL (for single image posts)"
    )
    parser.add_argument(
        "--images",
        type=int,
        help="Number of images for carousel (will use generated content)"
    )
    parser.add_argument(
        "-s", "--schedule",
        help="Schedule for later (format: 'YYYY-MM-DD HH:MM')"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test Instagram API connection"
    )
    
    args = parser.parse_args()
    
    # Create publisher
    try:
        publisher = InstagramPublisher()
    except Exception as e:
        print(f"{Fore.RED}❌ Error initializing Instagram publisher: {e}")
        print(f"{Fore.YELLOW}Make sure INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_BUSINESS_ACCOUNT_ID are set in .env")
        sys.exit(1)
    
    # Test connection
    if args.test_connection:
        success = publisher.test_connection()
        sys.exit(0 if success else 1)
    
    # Validate episode directory
    if not args.episode_dir:
        print(f"{Fore.RED}❌ Episode directory required (or use --test-connection)")
        sys.exit(1)
    
    if not os.path.exists(args.episode_dir):
        print(f"{Fore.RED}❌ Episode directory not found: {args.episode_dir}")
        sys.exit(1)
    
    # Read caption
    episode_path = Path(args.episode_dir)
    caption_file = episode_path / "formatted" / "instagram_caption_formatted.txt"
    
    if caption_file.exists():
        with open(caption_file, 'r', encoding='utf-8') as f:
            caption = f.read()
    else:
        print(f"{Fore.YELLOW}⚠️  No formatted caption found, using default")
        caption = "New episode of BandaWeb3! 🎙️\n\n#Web3 #Blockchain #BandaWeb3"
    
    # Prepare post data
    post_data = {
        "caption": caption,
        "type": args.type
    }
    
    if args.type == "image":
        if not args.image:
            print(f"{Fore.RED}❌ --image URL required for single image posts")
            sys.exit(1)
        post_data["image_url"] = args.image
    elif args.type == "carousel":
        if not args.images:
            print(f"{Fore.RED}❌ --images count required for carousel posts")
            sys.exit(1)
        
        # For now, require manual image URLs
        print(f"{Fore.YELLOW}⚠️  Please provide {args.images} image URLs (comma-separated):")
        image_urls_input = input("> ")
        image_urls = [url.strip() for url in image_urls_input.split(",")]
        
        if len(image_urls) != args.images:
            print(f"{Fore.RED}❌ Expected {args.images} URLs, got {len(image_urls)}")
            sys.exit(1)
        
        post_data["image_urls"] = image_urls
    
    # Schedule or publish
    if args.schedule:
        result = publisher.schedule_post(post_data, args.schedule)
    else:
        if args.type == "image":
            result = publisher.publish_image(post_data["image_url"], caption)
        else:
            result = publisher.publish_carousel(post_data["image_urls"], caption)
    
    # Print result
    if result.get("success"):
        print(f"\n{Fore.GREEN}✅ Success!")
        if "url" in result:
            print(f"{Fore.CYAN}Post URL: {result['url']}")
    else:
        print(f"\n{Fore.RED}❌ Failed to publish")
        sys.exit(1)


if __name__ == "__main__":
    main()

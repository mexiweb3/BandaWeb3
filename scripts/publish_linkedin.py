#!/usr/bin/env python3
"""
BandaWeb3 LinkedIn Publisher
Publishes content to LinkedIn using the LinkedIn API.

Usage:
    python3 publish_linkedin.py <content_file> [options]
    
Examples:
    # Test connection
    python3 publish_linkedin.py --test-connection
    
    # Publish article
    python3 publish_linkedin.py ../E075_*/content/article.md
    
    # Publish post
    python3 publish_linkedin.py ../E075_*/content/post_linkedin.txt --type post
    
    # Schedule for later
    python3 publish_linkedin.py ../E075_*/content/article.md --schedule "2024-12-06 09:00"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

class LinkedInPublisher:
    """Publishes content to LinkedIn."""
    
    def __init__(self):
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN not found in environment variables")
        
        self.api_base = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    def test_connection(self) -> bool:
        """Test LinkedIn API connection."""
        try:
            print(f"{Fore.CYAN}Testing LinkedIn API connection...")
            
            # Get user profile
            response = requests.get(
                f"{self.api_base}/me",
                headers=self.headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"{Fore.GREEN}✓ Connected to LinkedIn API")
                print(f"{Fore.CYAN}User ID: {user_data.get('id', 'Unknown')}")
                return True
            else:
                print(f"{Fore.RED}❌ Connection failed: {response.status_code}")
                print(f"{Fore.RED}Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error testing connection: {e}")
            return False
    
    def get_user_urn(self) -> str:
        """Get the user's URN (Uniform Resource Name)."""
        response = requests.get(
            f"{self.api_base}/me",
            headers=self.headers
        )
        
        if response.status_code == 200:
            user_id = response.json().get('id')
            return f"urn:li:person:{user_id}"
        else:
            raise Exception(f"Failed to get user URN: {response.text}")
    
    def publish_post(self, content: str, visibility: str = "PUBLIC") -> Dict:
        """
        Publish a text post to LinkedIn.
        
        Args:
            content: Post content (max 3000 chars)
            visibility: PUBLIC or CONNECTIONS
        
        Returns:
            Dict with post URL and metadata
        """
        try:
            print(f"{Fore.CYAN}Publishing post to LinkedIn...")
            
            # Validate content length
            if len(content) > 3000:
                print(f"{Fore.YELLOW}⚠️  Content exceeds 3000 chars, truncating...")
                content = content[:2997] + "..."
            
            # Get user URN
            author_urn = self.get_user_urn()
            
            # Prepare post data
            post_data = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            # Publish
            response = requests.post(
                f"{self.api_base}/ugcPosts",
                headers=self.headers,
                json=post_data
            )
            
            if response.status_code == 201:
                post_id = response.headers.get('X-RestLi-Id')
                print(f"{Fore.GREEN}✓ Post published successfully!")
                print(f"{Fore.CYAN}Post ID: {post_id}")
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "url": f"https://www.linkedin.com/feed/update/{post_id}",
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
            print(f"{Fore.RED}❌ Error publishing post: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def publish_article(self, title: str, content: str, visibility: str = "PUBLIC") -> Dict:
        """
        Publish an article to LinkedIn.
        
        Note: LinkedIn Article API requires special permissions.
        This method will post the article as a long-form text post.
        
        Args:
            title: Article title
            content: Article content
            visibility: PUBLIC or CONNECTIONS
        
        Returns:
            Dict with post URL and metadata
        """
        # Format article as post
        formatted_content = f"# {title}\n\n{content}"
        
        # Truncate if too long
        if len(formatted_content) > 3000:
            print(f"{Fore.YELLOW}⚠️  Article too long for LinkedIn post (max 3000 chars)")
            print(f"{Fore.YELLOW}Publishing first 3000 characters...")
            formatted_content = formatted_content[:2950] + "\n\n... [Read full article at link in comments]"
        
        return self.publish_post(formatted_content, visibility)
    
    def schedule_post(self, content: str, schedule_time: str) -> Dict:
        """
        Schedule a post for later.
        
        Note: LinkedIn API doesn't support native scheduling.
        This method saves the post data for later publishing via cron/n8n.
        
        Args:
            content: Post content
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
            post_data = {
                "platform": "linkedin",
                "content": content,
                "scheduled_time": scheduled_dt.isoformat(),
                "created_at": datetime.now().isoformat(),
                "status": "scheduled"
            }
            
            filename = f"linkedin_{scheduled_dt.strftime('%Y%m%d_%H%M')}.json"
            filepath = schedule_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, indent=2, ensure_ascii=False)
            
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
        description="Publish content to LinkedIn"
    )
    parser.add_argument(
        "content_file",
        nargs="?",
        help="Path to content file (.md or .txt)"
    )
    parser.add_argument(
        "-t", "--type",
        choices=["post", "article"],
        default="article",
        help="Content type (default: article)"
    )
    parser.add_argument(
        "-s", "--schedule",
        help="Schedule for later (format: 'YYYY-MM-DD HH:MM')"
    )
    parser.add_argument(
        "--test-connection",
        action="store_true",
        help="Test LinkedIn API connection"
    )
    parser.add_argument(
        "--visibility",
        choices=["PUBLIC", "CONNECTIONS"],
        default="PUBLIC",
        help="Post visibility (default: PUBLIC)"
    )
    
    args = parser.parse_args()
    
    # Create publisher
    try:
        publisher = LinkedInPublisher()
    except Exception as e:
        print(f"{Fore.RED}❌ Error initializing LinkedIn publisher: {e}")
        print(f"{Fore.YELLOW}Make sure LINKEDIN_ACCESS_TOKEN is set in .env file")
        sys.exit(1)
    
    # Test connection
    if args.test_connection:
        success = publisher.test_connection()
        sys.exit(0 if success else 1)
    
    # Validate content file
    if not args.content_file:
        print(f"{Fore.RED}❌ Content file required (or use --test-connection)")
        sys.exit(1)
    
    if not os.path.exists(args.content_file):
        print(f"{Fore.RED}❌ Content file not found: {args.content_file}")
        sys.exit(1)
    
    # Read content
    with open(args.content_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Schedule or publish
    if args.schedule:
        result = publisher.schedule_post(content, args.schedule)
    else:
        if args.type == "article":
            # Extract title from markdown
            lines = content.split('\n')
            title = lines[0].replace('#', '').strip() if lines else "Article"
            article_content = '\n'.join(lines[1:]).strip()
            result = publisher.publish_article(title, article_content, args.visibility)
        else:
            result = publisher.publish_post(content, args.visibility)
    
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

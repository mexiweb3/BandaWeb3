#!/usr/bin/env python3
"""
BandaWeb3 Content Formatter
Formats generated content for different social media platforms.

Usage:
    python3 format_for_platforms.py <episode_dir> [options]
    
Examples:
    # Format all content
    python3 format_for_platforms.py ../E075_2024-12-05 --all
    
    # Format only for Twitter
    python3 format_for_platforms.py ../E075_2024-12-05 --platform twitter
    
    # Format and copy to clipboard
    python3 format_for_platforms.py ../E075_2024-12-05 --platform twitter --clipboard
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import pyperclip
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class PlatformFormatter:
    """Formats content for different social media platforms."""
    
    def __init__(self, episode_dir: str, config_path: str = None):
        self.episode_dir = Path(episode_dir)
        self.content_dir = self.episode_dir / "content"
        
        # Load platform configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "platforms.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def format_twitter_thread(self) -> str:
        """Format content for Twitter thread."""
        thread_file = self.content_dir / "thread_x.json"
        
        if not thread_file.exists():
            raise FileNotFoundError(f"Thread file not found: {thread_file}")
        
        with open(thread_file, 'r', encoding='utf-8') as f:
            thread_data = json.load(f)
        
        # Extract tweets
        tweets = thread_data.get('tweets', [])
        
        if not tweets:
            raise ValueError("No tweets found in thread_x.json")
        
        # Format thread
        formatted = []
        total_tweets = len(tweets)
        
        for i, tweet in enumerate(tweets, 1):
            # Get tweet text
            text = tweet.get('text', '') if isinstance(tweet, dict) else str(tweet)
            
            # Validate character count
            max_chars = self.config['platforms']['twitter']['thread']['max_chars_per_tweet']
            if len(text) > max_chars:
                print(f"{Fore.YELLOW}⚠️  Tweet {i} exceeds {max_chars} chars ({len(text)} chars)")
            
            formatted.append(text)
        
        # Join with separators for easy copying
        output = "\n\n---\n\n".join(formatted)
        
        print(f"{Fore.GREEN}✓ Formatted {total_tweets} tweets for Twitter")
        print(f"{Fore.CYAN}Total thread length: {sum(len(t) for t in formatted)} characters")
        
        return output
    
    def format_linkedin_article(self) -> str:
        """Format content for LinkedIn article."""
        article_file = self.content_dir / "article.md"
        
        if not article_file.exists():
            raise FileNotFoundError(f"Article file not found: {article_file}")
        
        with open(article_file, 'r', encoding='utf-8') as f:
            article_content = f.read()
        
        # Validate character count
        max_chars = self.config['platforms']['linkedin']['article']['max_chars']
        recommended_chars = self.config['platforms']['linkedin']['article']['recommended_chars']
        
        char_count = len(article_content)
        
        if char_count > max_chars:
            print(f"{Fore.RED}❌ Article exceeds LinkedIn limit ({char_count}/{max_chars} chars)")
        elif char_count > recommended_chars:
            print(f"{Fore.YELLOW}⚠️  Article is longer than recommended ({char_count}/{recommended_chars} chars)")
        else:
            print(f"{Fore.GREEN}✓ Article length is optimal ({char_count} chars)")
        
        return article_content
    
    def format_linkedin_post(self) -> str:
        """Format content for LinkedIn short post."""
        post_file = self.content_dir / "post_linkedin.txt"
        
        if not post_file.exists():
            raise FileNotFoundError(f"LinkedIn post file not found: {post_file}")
        
        with open(post_file, 'r', encoding='utf-8') as f:
            post_content = f.read()
        
        # Validate character count
        max_chars = self.config['platforms']['linkedin']['post']['max_chars']
        recommended_chars = self.config['platforms']['linkedin']['post']['recommended_chars']
        
        char_count = len(post_content)
        
        if char_count > max_chars:
            print(f"{Fore.RED}❌ Post exceeds LinkedIn limit ({char_count}/{max_chars} chars)")
        elif char_count > recommended_chars:
            print(f"{Fore.YELLOW}⚠️  Post is longer than recommended ({char_count}/{recommended_chars} chars)")
        else:
            print(f"{Fore.GREEN}✓ Post length is optimal ({char_count} chars)")
        
        return post_content
    
    def format_instagram_caption(self, content_type: str = "carousel") -> str:
        """Format content for Instagram caption."""
        
        # Try to read from generated content or create from article
        caption_file = self.content_dir / "instagram_caption.txt"
        
        if caption_file.exists():
            with open(caption_file, 'r', encoding='utf-8') as f:
                caption = f.read()
        else:
            # Generate caption from article summary
            article_file = self.content_dir / "article.md"
            if article_file.exists():
                with open(article_file, 'r', encoding='utf-8') as f:
                    article = f.read()
                
                # Extract first paragraph as caption
                lines = article.split('\n')
                caption_lines = []
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        caption_lines.append(line)
                        if len('\n'.join(caption_lines)) > 300:
                            break
                
                caption = '\n'.join(caption_lines)
            else:
                raise FileNotFoundError("No Instagram caption or article found")
        
        # Add hashtags
        hashtags = self.config['platforms']['instagram']['post']['default_hashtags']
        hashtag_string = ' '.join(hashtags[:10])  # Use first 10 hashtags
        
        # Combine caption and hashtags
        full_caption = f"{caption}\n\n—\n\n{hashtag_string}"
        
        # Validate
        max_chars = self.config['platforms']['instagram']['post']['max_caption_chars']
        if len(full_caption) > max_chars:
            print(f"{Fore.YELLOW}⚠️  Caption exceeds Instagram limit ({len(full_caption)}/{max_chars} chars)")
        else:
            print(f"{Fore.GREEN}✓ Instagram caption formatted ({len(full_caption)} chars)")
        
        return full_caption
    
    def save_formatted_content(self, platform: str, content: str, suffix: str = ""):
        """Save formatted content to file."""
        output_dir = self.episode_dir / "formatted"
        output_dir.mkdir(exist_ok=True)
        
        filename = f"{platform}{suffix}_formatted.txt"
        output_file = output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"{Fore.GREEN}✓ Saved to: {output_file}")
        return output_file
    
    def format_all(self, copy_to_clipboard: bool = False) -> Dict[str, str]:
        """Format content for all platforms."""
        results = {}
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}Formatting content for all platforms...")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Twitter
        try:
            print(f"{Fore.BLUE}📱 Twitter/X Thread:")
            twitter_content = self.format_twitter_thread()
            self.save_formatted_content("twitter", twitter_content, "_thread")
            results['twitter'] = twitter_content
            print()
        except Exception as e:
            print(f"{Fore.RED}❌ Error formatting Twitter: {e}\n")
        
        # LinkedIn Article
        try:
            print(f"{Fore.BLUE}💼 LinkedIn Article:")
            linkedin_article = self.format_linkedin_article()
            self.save_formatted_content("linkedin", linkedin_article, "_article")
            results['linkedin_article'] = linkedin_article
            print()
        except Exception as e:
            print(f"{Fore.RED}❌ Error formatting LinkedIn article: {e}\n")
        
        # LinkedIn Post
        try:
            print(f"{Fore.BLUE}💼 LinkedIn Post:")
            linkedin_post = self.format_linkedin_post()
            self.save_formatted_content("linkedin", linkedin_post, "_post")
            results['linkedin_post'] = linkedin_post
            print()
        except Exception as e:
            print(f"{Fore.RED}❌ Error formatting LinkedIn post: {e}\n")
        
        # Instagram
        try:
            print(f"{Fore.BLUE}📸 Instagram Caption:")
            instagram_caption = self.format_instagram_caption()
            self.save_formatted_content("instagram", instagram_caption, "_caption")
            results['instagram'] = instagram_caption
            print()
        except Exception as e:
            print(f"{Fore.RED}❌ Error formatting Instagram: {e}\n")
        
        # Copy Twitter thread to clipboard by default
        if copy_to_clipboard and 'twitter' in results:
            pyperclip.copy(results['twitter'])
            print(f"{Fore.GREEN}✓ Twitter thread copied to clipboard!")
        
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}✓ Formatting complete! {len(results)} platforms formatted.")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Format BandaWeb3 content for social media platforms"
    )
    parser.add_argument(
        "episode_dir",
        help="Path to episode directory (e.g., ../E075_2024-12-05)"
    )
    parser.add_argument(
        "-p", "--platform",
        choices=["twitter", "linkedin", "instagram", "all"],
        default="all",
        help="Platform to format for (default: all)"
    )
    parser.add_argument(
        "-c", "--clipboard",
        action="store_true",
        help="Copy formatted content to clipboard"
    )
    parser.add_argument(
        "--config",
        help="Path to platforms.json config file"
    )
    
    args = parser.parse_args()
    
    # Validate episode directory
    if not os.path.exists(args.episode_dir):
        print(f"{Fore.RED}❌ Episode directory not found: {args.episode_dir}")
        sys.exit(1)
    
    # Create formatter
    formatter = PlatformFormatter(args.episode_dir, args.config)
    
    # Format content
    try:
        if args.platform == "all":
            results = formatter.format_all(copy_to_clipboard=args.clipboard)
        elif args.platform == "twitter":
            content = formatter.format_twitter_thread()
            formatter.save_formatted_content("twitter", content, "_thread")
            if args.clipboard:
                pyperclip.copy(content)
                print(f"{Fore.GREEN}✓ Copied to clipboard!")
        elif args.platform == "linkedin":
            article = formatter.format_linkedin_article()
            formatter.save_formatted_content("linkedin", article, "_article")
            post = formatter.format_linkedin_post()
            formatter.save_formatted_content("linkedin", post, "_post")
            if args.clipboard:
                pyperclip.copy(article)
                print(f"{Fore.GREEN}✓ Article copied to clipboard!")
        elif args.platform == "instagram":
            content = formatter.format_instagram_caption()
            formatter.save_formatted_content("instagram", content, "_caption")
            if args.clipboard:
                pyperclip.copy(content)
                print(f"{Fore.GREEN}✓ Copied to clipboard!")
        
        print(f"\n{Fore.GREEN}✅ Success! Content formatted and ready to publish.")
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

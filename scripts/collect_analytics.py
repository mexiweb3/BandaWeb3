#!/usr/bin/env python3
"""
BandaWeb3 Analytics Collector
Collects metrics from all social media platforms.

Usage:
    python3 collect_analytics.py [options]
    
Examples:
    # Collect metrics for specific episode
    python3 collect_analytics.py --episode 075 --days 7
    
    # Generate weekly report
    python3 collect_analytics.py --weekly-report
    
    # Export to CSV
    python3 collect_analytics.py --episode 075 --export csv
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
from colorama import Fore, Style, init
import pandas as pd

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / "config" / ".env")

class AnalyticsCollector:
    """Collects analytics from all platforms."""
    
    def __init__(self):
        # LinkedIn credentials
        self.linkedin_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        
        # Instagram credentials
        self.instagram_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        
        # Storage
        self.analytics_dir = Path(__file__).parent.parent / "analytics"
        self.analytics_dir.mkdir(exist_ok=True)
    
    def collect_linkedin_metrics(self, post_url: str = None) -> Dict:
        """Collect metrics from LinkedIn."""
        if not self.linkedin_token:
            print(f"{Fore.YELLOW}⚠️  LinkedIn token not configured")
            return {}
        
        try:
            print(f"{Fore.CYAN}Collecting LinkedIn metrics...")
            
            # Note: LinkedIn Analytics API requires special permissions
            # This is a placeholder for the actual implementation
            
            metrics = {
                "platform": "linkedin",
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "engagement_rate": 0.0,
                "collected_at": datetime.now().isoformat()
            }
            
            print(f"{Fore.YELLOW}⚠️  LinkedIn Analytics API requires enterprise access")
            print(f"{Fore.YELLOW}Please collect metrics manually from LinkedIn Analytics dashboard")
            
            return metrics
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error collecting LinkedIn metrics: {e}")
            return {}
    
    def collect_instagram_metrics(self, media_id: str = None) -> Dict:
        """Collect metrics from Instagram."""
        if not self.instagram_token or not self.instagram_account_id:
            print(f"{Fore.YELLOW}⚠️  Instagram credentials not configured")
            return {}
        
        try:
            print(f"{Fore.CYAN}Collecting Instagram metrics...")
            
            if media_id:
                # Get specific post metrics
                url = f"https://graph.facebook.com/v18.0/{media_id}/insights"
                params = {
                    "metric": "engagement,impressions,reach,saved",
                    "access_token": self.instagram_token
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json().get("data", [])
                    
                    metrics = {
                        "platform": "instagram",
                        "media_id": media_id,
                        "collected_at": datetime.now().isoformat()
                    }
                    
                    for metric in data:
                        name = metric.get("name")
                        values = metric.get("values", [])
                        if values:
                            metrics[name] = values[0].get("value", 0)
                    
                    print(f"{Fore.GREEN}✓ Instagram metrics collected")
                    return metrics
                else:
                    print(f"{Fore.RED}❌ Failed to get Instagram metrics: {response.status_code}")
                    return {}
            else:
                # Get account-level metrics
                url = f"https://graph.facebook.com/v18.0/{self.instagram_account_id}/insights"
                params = {
                    "metric": "impressions,reach,profile_views",
                    "period": "day",
                    "access_token": self.instagram_token
                }
                
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    print(f"{Fore.GREEN}✓ Instagram account metrics collected")
                    return response.json()
                else:
                    print(f"{Fore.RED}❌ Failed to get Instagram metrics")
                    return {}
                    
        except Exception as e:
            print(f"{Fore.RED}❌ Error collecting Instagram metrics: {e}")
            return {}
    
    def generate_report(self, episode_num: str, days: int = 7) -> str:
        """Generate analytics report for an episode."""
        
        # Find episode directory
        project_dir = Path(__file__).parent.parent
        episode_dir = None
        
        for dir_path in project_dir.parent.glob(f"E{episode_num}_*"):
            if dir_path.is_dir():
                episode_dir = dir_path
                break
        
        if not episode_dir:
            print(f"{Fore.RED}❌ Episode directory not found for E{episode_num}")
            return ""
        
        # Load published posts metadata
        metadata_file = episode_dir / "metadata.json"
        if not metadata_file.exists():
            print(f"{Fore.YELLOW}⚠️  No metadata found for episode {episode_num}")
            return ""
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Collect metrics
        all_metrics = {
            "episode": episode_num,
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "platforms": {}
        }
        
        # LinkedIn
        if "linkedin_post_id" in metadata:
            linkedin_metrics = self.collect_linkedin_metrics(metadata["linkedin_post_id"])
            all_metrics["platforms"]["linkedin"] = linkedin_metrics
        
        # Instagram
        if "instagram_media_id" in metadata:
            instagram_metrics = self.collect_instagram_metrics(metadata["instagram_media_id"])
            all_metrics["platforms"]["instagram"] = instagram_metrics
        
        # Save metrics
        metrics_file = self.analytics_dir / f"E{episode_num}_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)
        
        print(f"{Fore.GREEN}✓ Metrics saved to {metrics_file}")
        
        # Generate markdown report
        report = self._generate_markdown_report(all_metrics)
        
        report_file = self.analytics_dir / f"E{episode_num}_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"{Fore.GREEN}✓ Report saved to {report_file}")
        
        return report
    
    def _generate_markdown_report(self, metrics: Dict) -> str:
        """Generate markdown report from metrics."""
        
        episode = metrics.get("episode", "Unknown")
        generated_at = metrics.get("generated_at", "")
        period = metrics.get("period_days", 7)
        
        report = f"""# Analytics Report - Episode {episode}

**Generated:** {generated_at}  
**Period:** Last {period} days

---

## Platform Performance

"""
        
        platforms = metrics.get("platforms", {})
        
        # LinkedIn
        if "linkedin" in platforms:
            linkedin = platforms["linkedin"]
            report += f"""### 💼 LinkedIn

- **Views:** {linkedin.get('views', 'N/A')}
- **Likes:** {linkedin.get('likes', 'N/A')}
- **Comments:** {linkedin.get('comments', 'N/A')}
- **Shares:** {linkedin.get('shares', 'N/A')}
- **Engagement Rate:** {linkedin.get('engagement_rate', 'N/A')}%

"""
        
        # Instagram
        if "instagram" in platforms:
            instagram = platforms["instagram"]
            report += f"""### 📸 Instagram

- **Impressions:** {instagram.get('impressions', 'N/A')}
- **Reach:** {instagram.get('reach', 'N/A')}
- **Engagement:** {instagram.get('engagement', 'N/A')}
- **Saved:** {instagram.get('saved', 'N/A')}

"""
        
        # Summary
        report += """---

## Summary

"""
        
        total_engagement = 0
        total_reach = 0
        
        for platform, data in platforms.items():
            engagement = data.get('engagement', 0) or data.get('likes', 0)
            reach = data.get('reach', 0) or data.get('views', 0)
            total_engagement += engagement
            total_reach += reach
        
        report += f"""- **Total Reach:** {total_reach:,}
- **Total Engagement:** {total_engagement:,}
- **Overall Engagement Rate:** {(total_engagement / total_reach * 100) if total_reach > 0 else 0:.2f}%

---

*Note: Metrics collected automatically. Some platforms may require manual data entry.*
"""
        
        return report
    
    def export_to_csv(self, episode_num: str):
        """Export metrics to CSV."""
        
        metrics_file = self.analytics_dir / f"E{episode_num}_metrics.json"
        
        if not metrics_file.exists():
            print(f"{Fore.RED}❌ Metrics file not found. Run collection first.")
            return
        
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)
        
        # Flatten metrics for CSV
        rows = []
        for platform, data in metrics.get("platforms", {}).items():
            row = {
                "episode": metrics.get("episode"),
                "platform": platform,
                "collected_at": data.get("collected_at", ""),
                **data
            }
            rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Export
        csv_file = self.analytics_dir / f"E{episode_num}_metrics.csv"
        df.to_csv(csv_file, index=False)
        
        print(f"{Fore.GREEN}✓ Exported to {csv_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Collect analytics from social media platforms"
    )
    parser.add_argument(
        "-e", "--episode",
        help="Episode number (e.g., 075)"
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)"
    )
    parser.add_argument(
        "--weekly-report",
        action="store_true",
        help="Generate weekly report for all recent episodes"
    )
    parser.add_argument(
        "--export",
        choices=["csv", "json"],
        help="Export format"
    )
    
    args = parser.parse_args()
    
    collector = AnalyticsCollector()
    
    if args.weekly_report:
        print(f"{Fore.CYAN}Generating weekly report...")
        print(f"{Fore.YELLOW}⚠️  Weekly report feature coming soon")
    elif args.episode:
        report = collector.generate_report(args.episode, args.days)
        
        if args.export == "csv":
            collector.export_to_csv(args.episode)
        
        print(f"\n{Fore.GREEN}✅ Analytics collection complete!")
    else:
        print(f"{Fore.RED}❌ Please specify --episode or --weekly-report")
        sys.exit(1)


if __name__ == "__main__":
    main()

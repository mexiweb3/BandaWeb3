# Publishing Workflow Guide

Complete guide for publishing BandaWeb3 content across all platforms using the semi-automated workflow.

---

## 🎯 Overview

This workflow automates 95% of content distribution while keeping costs low (~$100/month vs $5,000/month with X API Pro).

**What's Automated:**
- ✅ Content formatting for all platforms
- ✅ LinkedIn publishing
- ✅ Instagram publishing (with manual image URLs)
- ✅ Analytics collection

**What's Manual:**
- 📱 X/Twitter posting (via Typefully/Buffer)

---

## 📋 Prerequisites

### Required Tools
1. **Python 3.11+** with dependencies installed
2. **API Credentials** (see [API_SETUP.md](API_SETUP.md))
   - LinkedIn API (Client ID, Secret, Access Token)
   - Instagram Graph API (Access Token, Business Account ID)
3. **Optional:** Typefully ($12/month) or Buffer ($15/month) for X/Twitter scheduling

### Environment Setup

```bash
# 1. Install dependencies
cd bandaweb3-automation
pip install -r requirements.txt

# 2. Configure environment variables
cp config/.env.example config/.env
# Edit .env with your API credentials

# 3. Make scripts executable
chmod +x scripts/*.sh
```

---

## 🚀 Quick Start

### Option 1: One-Command Publishing (Recommended)

```bash
# Format and publish everything
./scripts/publish_all.sh 075

# Dry run (format only, no publishing)
./scripts/publish_all.sh 075 --dry-run

# Schedule for later
./scripts/publish_all.sh 075 --schedule "2024-12-06 09:00"
```

### Option 2: Step-by-Step

```bash
# 1. Format content
python3 scripts/format_for_platforms.py ../E075_2024-12-05 --all --clipboard

# 2. Publish to LinkedIn
python3 scripts/publish_linkedin.py ../E075_*/content/article.md

# 3. Publish to Instagram
python3 scripts/publish_instagram.py ../E075_* --type carousel

# 4. Paste Twitter thread from clipboard to Typefully
```

---

## 📱 Platform-Specific Workflows

### X/Twitter (Semi-Automated)

**Why not fully automated?**  
X API Pro costs $5,000/month. Instead, we use Typefully ($12/month) for scheduling.

**Workflow:**
1. Run formatter (thread is auto-copied to clipboard)
2. Open Typefully or Buffer
3. Paste thread (Ctrl+V / Cmd+V)
4. Review and schedule
5. Publish

**Tools:**
- **Typefully** (Recommended): $12/month, best for threads
- **Buffer**: $15/month, multi-platform
- **Hypefury**: $29/month, advanced features

### LinkedIn (Fully Automated)

**Workflow:**
```bash
# Publish article immediately
python3 scripts/publish_linkedin.py ../E075_*/content/article.md

# Schedule for tomorrow at 9am
python3 scripts/publish_linkedin.py ../E075_*/content/article.md --schedule "2024-12-06 09:00"

# Publish short post
python3 scripts/publish_linkedin.py ../E075_*/content/post_linkedin.txt --type post
```

**Best Practices:**
- Post articles on Tuesday-Thursday mornings (8-10am)
- Use professional tone
- Limit hashtags to 3-5
- Include call-to-action

### Instagram (Semi-Automated)

**Workflow:**
```bash
# 1. Upload images to public host (Imgur, Cloudinary, etc.)
# 2. Get public URLs

# 3. Publish carousel
python3 scripts/publish_instagram.py ../E075_* --type carousel
# Enter image URLs when prompted

# 4. Or publish single image
python3 scripts/publish_instagram.py ../E075_* --type image --image "https://..."
```

**Image Requirements:**
- Format: JPG or PNG
- Aspect ratio: 1:1 (square) or 4:5 (portrait)
- Max size: 8MB
- Publicly accessible URL

**Best Practices:**
- Post at 10am, 2pm, or 7pm
- Use 10-15 hashtags
- Include emoji in caption
- Engage with comments within first hour

---

## 📊 Analytics Collection

### Collect Metrics

```bash
# Collect metrics for specific episode (after 7 days)
python3 scripts/collect_analytics.py --episode 075 --days 7

# Export to CSV
python3 scripts/collect_analytics.py --episode 075 --export csv
```

### Metrics Collected

**LinkedIn:**
- Views
- Likes
- Comments
- Shares
- Engagement rate

**Instagram:**
- Impressions
- Reach
- Engagement
- Saves

**Output:**
- `analytics/E075_metrics.json` - Raw metrics
- `analytics/E075_report.md` - Formatted report
- `analytics/E075_metrics.csv` - CSV export

---

## 🗓️ Recommended Publishing Schedule

### Thursday (Space Day)

**11:00 AM** - Pre-Space
- Tweet announcement
- Instagram story

**12:00 PM** - During Space
- Live tweets with quotes
- Engage with participants

**3:00 PM** - Post-Space
- Run content generation
- Format content
- Review and edit

**6:00 PM** - Initial Publishing
- Publish LinkedIn article
- Schedule Twitter thread for Friday 9am
- Prepare Instagram carousel

### Friday

**9:00 AM** - Twitter
- Thread goes live (scheduled)
- Monitor and engage

**12:00 PM** - Instagram
- Publish carousel
- Post to stories

**3:00 PM** - Engagement
- Respond to comments
- Share to relevant groups

### Saturday-Sunday

**10:00 AM** - Additional Content
- LinkedIn short posts
- Instagram stories
- Twitter quotes

### Following Thursday

**9:00 AM** - Analytics
- Collect metrics
- Generate report
- Analyze performance

---

## 🔧 Troubleshooting

### "API Key not found"
```bash
# Check .env file exists and is loaded
cat config/.env | grep API_KEY

# Verify environment variables
python3 -c "from dotenv import load_dotenv; import os; load_dotenv('config/.env'); print(os.getenv('LINKEDIN_ACCESS_TOKEN'))"
```

### "Content file not found"
```bash
# Verify episode directory structure
ls -la ../E075_*/content/

# Expected files:
# - thread_x.json
# - article.md
# - post_linkedin.txt
```

### "Character limit exceeded"
- Edit content manually in `content/` directory
- Re-run formatter
- Content will be truncated with warning

### LinkedIn: "Invalid access token"
- Token may have expired
- Regenerate token (see [API_SETUP.md](API_SETUP.md))
- Update `.env` file

### Instagram: "Image URL not accessible"
- Ensure image is publicly accessible
- Try opening URL in incognito browser
- Use different hosting service (Imgur, Cloudinary)

---

## 💡 Tips & Best Practices

### Content Quality
1. **Always review before publishing** - AI-generated content needs human touch
2. **Customize for each platform** - Don't just copy-paste
3. **Add personal insights** - Share your unique perspective
4. **Use visuals** - Images increase engagement 2-3x

### Timing
1. **LinkedIn:** Tuesday-Thursday, 8-10am
2. **Instagram:** Daily, 10am, 2pm, or 7pm
3. **Twitter:** Multiple times daily, peak at 9am, 12pm, 6pm

### Engagement
1. **Respond within 1 hour** to first comments
2. **Ask questions** to encourage discussion
3. **Tag relevant people** (speakers, projects mentioned)
4. **Share to groups** (Web3, blockchain, LATAM communities)

### Analytics
1. **Track consistently** - Same day each week
2. **Compare episodes** - Identify what works
3. **Adjust strategy** - Based on data, not feelings
4. **Focus on engagement** - Not just reach

---

## 📞 Support

### Common Issues
- See [Troubleshooting](#troubleshooting) section above
- Check [API_SETUP.md](API_SETUP.md) for credential issues

### Need Help?
1. Check error messages carefully
2. Verify all prerequisites are met
3. Review logs in `logs/automation.log`
4. Test API connections with `--test-connection` flag

---

**Last Updated:** December 2024  
**Version:** 1.0

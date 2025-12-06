# 🚀 Quick Reference - Publishing Workflow

## One-Line Commands

```bash
# Complete workflow (format + publish)
./scripts/publish_all.sh 075

# Dry run (test without publishing)
./scripts/publish_all.sh 075 --dry-run

# Format only
python3 scripts/format_for_platforms.py ../E075_* --all --clipboard

# Publish to LinkedIn
python3 scripts/publish_linkedin.py ../E075_*/content/article.md

# Publish to Instagram
python3 scripts/publish_instagram.py ../E075_* --type carousel

# Collect analytics
python3 scripts/collect_analytics.py --episode 075 --days 7
```

---

## File Structure

```
bandaweb3-automation/
├── scripts/
│   ├── format_for_platforms.py    # Format content for all platforms
│   ├── publish_linkedin.py         # LinkedIn auto-publisher
│   ├── publish_instagram.py        # Instagram auto-publisher
│   ├── publish_all.sh              # One-command orchestrator
│   └── collect_analytics.py        # Analytics collector
│
├── config/
│   ├── .env.example                # Environment variables template
│   └── platforms.json              # Platform-specific rules
│
└── docs/
    ├── PUBLISHING_WORKFLOW.md      # Complete publishing guide
    └── API_SETUP.md                # API credentials setup
```

---

## Workflow Steps

### 1. Generate Content (Existing)
```bash
./scripts/process_episode.sh 075 space.mp3
```

### 2. Format Content (NEW)
```bash
python3 scripts/format_for_platforms.py ../E075_* --all --clipboard
```

### 3. Publish (NEW)

**LinkedIn (Auto):**
```bash
python3 scripts/publish_linkedin.py ../E075_*/content/article.md
```

**Instagram (Auto):**
```bash
python3 scripts/publish_instagram.py ../E075_* --type carousel
```

**X/Twitter (Manual - 30 seconds):**
1. Open Typefully
2. Paste (Ctrl+V)
3. Schedule

### 4. Analytics (NEW)
```bash
# After 7 days
python3 scripts/collect_analytics.py --episode 075 --days 7
```

---

## Cost Breakdown

| Service | Cost/Month |
|---------|------------|
| Whisper API | $43 |
| Claude API | $30-50 |
| Typefully | $12 |
| **TOTAL** | **$85-105** |

**vs X API Pro: $5,000/month**  
**Savings: $4,915/month** 💰

---

## Setup Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy `.env.example` to `.env`
- [ ] Add OpenAI API key
- [ ] Add Anthropic API key
- [ ] Add email credentials
- [ ] (Optional) Add LinkedIn API credentials
- [ ] (Optional) Add Instagram API credentials
- [ ] (Optional) Sign up for Typefully

---

## Documentation

- **[PUBLISHING_WORKFLOW.md](docs/PUBLISHING_WORKFLOW.md)** - Complete guide
- **[API_SETUP.md](docs/API_SETUP.md)** - API credentials setup
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Quick start guide

---

## Support

Test API connections:
```bash
python3 scripts/publish_linkedin.py --test-connection
python3 scripts/publish_instagram.py --test-connection
```

Check logs:
```bash
tail -f logs/automation.log
```

---

**Ready to publish!** 🎉

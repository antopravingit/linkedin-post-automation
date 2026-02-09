# LinkedIn AI Content Curator

Automated system that discovers AI articles, generates LinkedIn posts, and auto-posts to your LinkedIn profile.

## Features
- Auto-discovers articles from 16 top AI/tech news sources
- Selects top 5 articles (mix of technical + general)
- Creates Notion pages with summaries and LinkedIn posts
- Sends email notification with article links
- Auto-posts approved articles to LinkedIn every 2 hours

**Time investment**: ~10 minutes per week for 5 high-quality LinkedIn posts!

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env` and fill in your API keys:
- `OPENAI_API_KEY` - OpenAI API key for AI generation
- `NOTION_API_KEY` - Notion integration token
- `NOTION_DATABASE_ID` - Your Notion database ID
- `LINKEDIN_CLIENT_ID` - LinkedIn app client ID
- `LINKEDIN_CLIENT_SECRET` - LinkedIn app client secret
- `SMTP_EMAIL` / `SMTP_PASSWORD` - Gmail for notifications
- `NOTIFICATION_EMAIL` - Where to receive notifications

### 3. Run the Curator
```bash
python linkedin_curator.py
```

### 4. Review & Approve
Check your email for Notion links, review articles, approve favorites in Notion.

### 5. Auto-Post
The auto-poster posts approved articles to LinkedIn every 2 hours.

## Project Structure
```
Core System (11 files):
├── linkedin_curator.py          # Main entry point
├── linkedin_oauth.py             # LinkedIn OAuth setup
├── linkedin_poster.py             # Posts to LinkedIn
├── linkedin_integration.py        # Notion + LinkedIn integration
├── notion_integration.py          # Notion page creation
├── article_discovery.py           # RSS feed discovery
├── article_fetcher.py             # Article content fetching
├── article_selector.py            # Article scoring/selection
├── ai_generator.py                # AI content generation
└── draft_generator.py             # Template-based generation
└── requirements.txt               # Dependencies

Tools (6 files):
├── tools/approve.py               # CLI approval tool
├── tools/extract_notion_links.py  # Extract Notion URLs
├── tools/send_notification.py     # Email notifications
├── tools/send_failure_notification.py  # Failure alerts
├── tools/auto_poster.py           # Auto-posting script
└── tools/cleanup_notion.py        # Cleanup old articles

GitHub Actions:
└── .github/workflows/             # Automated workflows
    ├── generate-content.yml        # Auto-generate content (Mondays 9 AM)
    ├── auto-post.yml               # Auto-post every 2 hours
    └── cleanup.yml                 # Monthly database cleanup
```

## Two Modes of Operation

### Mode 1: Weekly Automation (Default) 🔄

**Monday Morning (Automatic)**:
- GitHub Actions runs at 9 AM
- Discovers 50+ articles from 16 sources
- AI selects top 5 (mix of technical + general)
- Creates Notion pages
- Sends you email

**Your Part (10 minutes)**:
- Review email
- Click Notion links
- Approve 2-3 favorites

**Throughout Week (Automatic)**:
- Auto-poster posts approved articles every 2 hours

**Cost**: ~$3/month | **Speed**: Fast | **Best for**: Regular posting

---

### Mode 2: On-Demand Agent (When You Need Focus) 🎯

**When you want specific topics**:
```bash
# Find posts about a specific topic
python agent_curator.py --topic "AI regulation" --count 3

# Interactive mode
python agent_curator.py
# → Enter topic, select style, get targeted posts
```

**Use cases**:
- "I need posts about AI ethics this week"
- "Find me technical LLM tutorials"
- "What's new in AI for healthcare?"

**Cost**: $0.50-1 per search | **Speed**: Moderate | **Best for**: Targeted content

## 16 News Sources
MIT Technology Review AI, Ars Technica, TechCrunch AI, VentureBeat AI, AI News, Towards Data Science, Wired, The Verge, Nature AI, Science Daily AI, Fast Company, Harvard Business Review Technology, ArXiv AI, Machine Learning Mastery, KDnuggets, The Gradient, DeepLearning.AI

## Notification System

You'll receive email notifications for:
- ✅ **Success**: 5 articles ready for review (Monday morning)
- ❌ **Failure**: Immediate alert if anything breaks

## Database Cleanup

Automatic cleanup runs **monthly** (1st of each month):
- Deletes "Not Reviewed" articles older than 30 days
- Deletes "Draft" articles older than 30 days
- Keeps "Approved" and "Posted" articles forever

**Manual cleanup:**
```bash
python tools/cleanup_notion.py
```

Interactive options:
- Choose age threshold (days)
- Filter by status
- Dry-run mode to preview before deleting

## Summary
**You invest**: 10 minutes per week
**You get**: 5 high-quality LinkedIn posts about proven AI implementations
**Time saved**: ~93% compared to manual posting

Enjoy your automated LinkedIn presence! 🚀

#!/usr/bin/env python3
"""
Agent-Based Content Curator - For targeted, on-demand content discovery.

Use this when you want specific topics or types of posts:
- "Find me posts about AI regulation"
- "I need technical tutorials this week"
- "What's new in LLMs?"

For regular automation, use linkedin_curator.py instead.
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def agent_curator(topic: str, count: int = 3, style: str = "mixed"):
    """
    Use an AI agent to find and curate content on a specific topic.

    Args:
        topic: Specific topic to search for (e.g., "AI regulation", "LLM research")
        count: Number of articles to generate (default: 3)
        style: Content style - "technical", "general", or "mixed"

    Returns:
        True if successful, False otherwise
    """
    try:
        import openai
    except ImportError:
        print("[!] openai package not installed. Run: pip install openai")
        return False

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[!] OPENAI_API_KEY environment variable not set")
        return False

    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_db_id = os.getenv("NOTION_DATABASE_ID")
    if not notion_api_key or not notion_db_id:
        print("[!] NOTION_API_KEY or NOTION_DATABASE_ID not set")
        return False

    print(f"\n{'='*70}")
    print(f"🤖 AGENT CURATOR - Targeted Content Discovery")
    print(f"{'='*70}")
    print(f"Topic: {topic}")
    print(f"Count: {count} articles")
    print(f"Style: {style}")
    print(f"{'='*70}\n")

    # Step 1: Agent searches for relevant content
    print("[Agent] Searching web for recent articles about: {topic}...")
    articles = search_articles(topic, count * 3)  # Get more, then filter

    if not articles:
        print(f"[!] No articles found for topic: {topic}")
        return False

    print(f"[+] Found {len(articles)} articles")

    # Step 2: Agent analyzes and selects best ones
    print(f"\n[Agent] Analyzing and selecting top {count} articles...")
    selected = agent_select_articles(articles, topic, count, style)

    # Step 3: Generate approval packs and save to Notion
    print(f"\n[Agent] Generating LinkedIn posts for selected articles...")
    from notion_integration import save_to_notion
    from ai_generator import generate_with_openai

    approval_pack = generate_with_openai(selected)

    # Save each article to Notion
    saved_count = 0
    from notion_client import Client
    notion = Client(auth=notion_api_key)

    # Parse approval pack and create pages
    import re
    article_blocks = re.split(r'ARTICLE \d+:', approval_pack)

    for i, block in enumerate(article_blocks[1:], 1):  # Skip first empty split
        try:
            # Extract title
            title_match = re.search(r'Article Title: (.+)', block)
            title = title_match.group(1).strip() if title_match else f"{topic} Article {i}"

            # Extract URL
            url_match = re.search(r'Article URL: (https?://[^\s]+)', block)
            url = url_match.group(1).strip() if url_match else ""

            # Extract LinkedIn post
            linkedin_match = re.search(r'LINKEDIN POST:\s*\n(.+?)(?=ARTICLE \d+|WHY THIS MATTERS|$)', block, re.DOTALL)
            linkedin_post = linkedin_match.group(1).strip() if linkedin_match else block[-500:]

            # Create Notion page
            notion.pages.create(
                parent={"database_id": notion_db_id},
                properties={
                    "Title": {
                        "title": [{"text": {"content": title}}]
                    },
                    "Status": {
                        "status": {"name": "Draft"}
                    }
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": linkedin_post}}]
                        }
                    }
                ]
            )
            saved_count += 1
            print(f"  [+] Saved: {title[:50]}...")

        except Exception as e:
            print(f"  [!] Failed to save article {i}: {e}")

    print(f"\n{'='*70}")
    print(f"✅ Agent completed! Generated {saved_count} articles about '{topic}'")
    print(f"{'='*70}")
    print(f"\nNext steps:")
    print(f"  1. Check your Notion database")
    print(f"  2. Review the articles")
    print(f"  3. Change status to 'Approved' to post")
    print(f"  4. Auto-poster will publish them\n")

    return True


def search_articles(topic: str, max_results: int = 10) -> list[dict]:
    """
    Agent searches the web for recent articles about the topic.

    Args:
        topic: Topic to search for
        max_results: Maximum number of results to return

    Returns:
        List of article dictionaries with 'title', 'url', 'text'
    """
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except ImportError:
        return []

    # Use AI to find relevant article URLs
    # Note: In production, you'd integrate a real search API
    # For now, we'll use a curated list of AI/tech sources

    print(f"[Agent] Suggesting search strategies for: {topic}")

    # Simulate finding articles (in real use, integrate search API)
    suggestions = f"""
Based on the topic "{topic}", here are recommended sources to check:

1. Google News: https://news.google.com/search?q={topic.replace(' ', '+'}+AI
2. TechCrunch: https://techcrunch.com/tag/{topic.lower().replace(' ', '-')}
3. MIT Technology Review: Site search for {topic}
4. ArXiv.org: https://arxiv.org/search/?query={topic.replace(' ', '+')}
5. VentureBeat: https://venturebeat.com/category/ai/
6. Towards Data Science: Medium search for {topic}

Please paste 3-5 article URLs from these sources, and I'll analyze them.
"""

    print(suggestions)

    # For demo, return empty - user would provide URLs
    # In production, integrate a search API
    return []


def agent_select_articles(articles: list[dict], topic: str, count: int, style: str) -> list[dict]:
    """
    Agent selects the best articles for the given topic and style.

    Args:
        articles: List of candidate articles
        topic: Target topic
        count: Number to select
        style: Content style preference

    Returns:
        List of selected articles
    """
    # For now, return all articles
    # In production, use AI to score and rank
    return articles[:count]


def interactive_mode():
    """Interactive mode for agent curator."""
    print("\n" + "="*70)
    print("AGENT CURATOR - Interactive Mode")
    print("="*70)

    topic = input("\nWhat topic are you looking for? ").strip()

    if not topic:
        print("[!] Topic is required")
        return 1

    count_input = input("How many articles? (default 3): ").strip()
    count = int(count_input) if count_input else 3

    print("\nStyle options:")
    print("  1. Technical (research, code, implementation)")
    print("  2. General (business, trends, overview)")
    print("  3. Mixed (balance of both)")

    style_choice = input("\nSelect style (default 3): ").strip() or "3"
    style_map = {"1": "technical", "2": "general", "3": "mixed"}
    style = style_map.get(style_choice, "mixed")

    print()

    success = agent_curator(topic, count, style)
    return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Agent-based content curator for targeted discovery'
    )
    parser.add_argument('--topic', type=str, help='Topic to search for')
    parser.add_argument('--count', type=int, default=3, help='Number of articles (default 3)')
    parser.add_argument('--style', type=str, default='mixed',
                        choices=['technical', 'general', 'mixed'],
                        help='Content style (default mixed)')

    args = parser.parse_args()

    # If no topic provided, run interactive mode
    if not args.topic:
        sys.exit(interactive_mode())
    else:
        success = agent_curator(args.topic, args.count, args.style)
        sys.exit(0 if success else 1)

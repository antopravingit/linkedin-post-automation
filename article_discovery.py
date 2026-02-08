#!/usr/bin/env python3
"""
Article Discovery - Automatically finds interesting AI articles from various sources.
Uses RSS feeds from AI/tech news websites to suggest articles.
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass

from article_fetcher import Article, fetch_article


# AI news sources with RSS feeds
AI_NEWS_SOURCES = [
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topnews.rss?section=artificial-intelligence",
        "topic": "AI"
    },
    {
        "name": "Arstechnica AI",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lag",
        "topic": "Technology"
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "topic": "AI"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/ai/feed/",
        "topic": "AI"
    },
    {
        "name": "AI News",
        "url": "https://artificialintelligence-news.com/feed/",
        "topic": "AI"
    },
    {
        "name": "Towards Data Science",
        "url": "https://towardsdatascience.com/feed",
        "topic": "Data Science"
    },
    {
        "name": "Wired",
        "url": "https://www.wired.com/feed/rss",
        "topic": "Technology"
    },
    {
        "name": "The Verge",
        "url": "https://www.theverge.com/rss/index.xml",
        "topic": "Technology"
    },
    {
        "name": "Nature AI",
        "url": "https://www.nature.com/nmachis/rss/nmachis.iframe",
        "topic": "Research"
    },
    {
        "name": "Science Daily AI",
        "url": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
        "topic": "Research"
    },
    {
        "name": "Fast Company",
        "url": "https://www.fastcompany.com/rss",
        "topic": "Business"
    },
    {
        "name": "Harvard Business Review Technology",
        "url": "https://hbr.org/feed/technology-innovation",
        "topic": "Business"
    },
    {
        "name": "ArXiv AI (Recent papers)",
        "url": "http://export.arxiv.org/api/query?search_query=cat:cs.AI+cat:cs.LG+cat:cs.CL&sortBy=submittedDate&sortOrder=descending&max_results=10",
        "topic": "Research"
    },
    {
        "name": "Machine Learning Mastery",
        "url": "https://machinelearningmastery.com/feed/",
        "topic": "Technical"
    },
    {
        "name": "KDnuggets",
        "url": "https://www.kdnuggets.com/feed",
        "topic": "Data Science"
    },
    {
        "name": "The Gradient (Publication)",
        "url": "https://thegradient.pub/rss.xml",
        "topic": "Research"
    },
    {
        "name": "DeepLearning.AI",
        "url": "https://www.deeplearning.ai/feed/",
        "topic": "Technical"
    }
]


@dataclass
class DiscoveredArticle:
    """Article discovered from RSS feed."""
    title: str
    url: str
    summary: str
    published: Optional[datetime]
    source: str

    def __post_init__(self):
        """Convert published date to datetime object if it's a string."""
        if isinstance(self.published, str):
            try:
                self.published = datetime.fromisoformat(self.published.replace('Z', '+00:00'))
            except:
                self.published = None


def fetch_rss_articles(source_url: str, source_name: str, max_articles: int = 10, days_back: int = 7) -> List[DiscoveredArticle]:
    """
    Fetch articles from an RSS feed.

    Args:
        source_url: URL of the RSS feed
        source_name: Name of the source
        max_articles: Maximum number of articles to fetch
        days_back: Only fetch articles from last N days

    Returns:
        List of DiscoveredArticle objects
    """
    try:
        feed = feedparser.parse(source_url)
        articles = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        for entry in feed.entries[:max_articles * 2]:  # Get more than needed, we'll filter
            # Parse published date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime(*entry.updated_parsed[:6])

            # Skip if too old
            if published and published < cutoff_date:
                continue

            # Get URL
            url = entry.link
            if not url:
                continue

            # Get title
            title = entry.title
            if not title:
                continue

            # Get summary
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description

            # Clean summary (remove HTML tags)
            import re
            summary = re.sub('<[^<]+?>', '', summary)
            summary = summary[:500]  # Truncate to 500 chars

            articles.append(DiscoveredArticle(
                title=title,
                url=url,
                summary=summary.strip(),
                published=published,
                source=source_name
            ))

            if len(articles) >= max_articles:
                break

        return articles

    except Exception as e:
        print(f"[!] Error fetching from {source_name}: {e}")
        return []


def discover_articles(max_per_source: int = 5, total_limit: int = 20, days_back: int = 7) -> List[DiscoveredArticle]:
    """
    Discover articles from multiple AI news sources.

    Args:
        max_per_source: Maximum articles to fetch per source
        total_limit: Maximum total articles to return
        days_back: Only fetch articles from last N days

    Returns:
        List of DiscoveredArticle objects, sorted by publication date (newest first)
    """
    print("\n[*] Discovering articles from AI news sources...")
    print(f"    Looking for articles from the last {days_back} days")
    print(f"    Maximum {total_limit} articles")
    print()

    all_articles = []

    for source in AI_NEWS_SOURCES:
        print(f"[*] Fetching from {source['name']}...")
        articles = fetch_rss_articles(
            source['url'],
            source['name'],
            max_articles=max_per_source,
            days_back=days_back
        )
        print(f"    Found {len(articles)} articles")
        all_articles.extend(articles)

    # Sort by publication date (newest first)
    all_articles.sort(key=lambda x: x.published or datetime.min, reverse=True)

    # Limit total
    all_articles = all_articles[:total_limit]

    print(f"\n[+] Total articles discovered: {len(all_articles)}")

    return all_articles


def fetch_and_analyze_discovered(discovered_articles: List[DiscoveredArticle]) -> List[Article]:
    """
    Fetch full content for discovered articles.

    Args:
        discovered_articles: List of DiscoveredArticle objects

    Returns:
        List of Article objects with full content
    """
    articles = []

    print(f"\n[*] Fetching full content for {len(discovered_articles)} articles...")
    print()

    for i, discovered in enumerate(discovered_articles, 1):
        print(f"[{i}/{len(discovered_articles)}] {discovered.title[:60]}...")

        article = fetch_article(discovered.url)

        if article:
            articles.append(article)
            print(f"    [+] Fetched ({article.word_count()} words)")
        else:
            print(f"    [!] Skipped (fetch failed)")

    print(f"\n[+] Successfully fetched {len(articles)}/{len(discovered_articles)} articles")

    return articles


def discover_and_fetch(max_articles: int = 20) -> List[Article]:
    """
    Complete discovery pipeline: discover RSS articles and fetch full content.

    Args:
        max_articles: Maximum number of articles to return

    Returns:
        List of Article objects ready for AI analysis
    """
    # Discover from RSS feeds
    discovered = discover_articles(
        max_per_source=8,  # More per source to get better variety
        total_limit=max_articles * 2,  # Get more, we'll filter after fetching
        days_back=7
    )

    if not discovered:
        print("\n[!] No articles discovered. Try:")
        print("    1. Checking internet connection")
        print("    2. Running again later (RSS feeds may be temporarily down)")
        return []

    # Fetch full content
    articles = fetch_and_analyze_discovered(discovered)

    return articles


if __name__ == "__main__":
    # Test article discovery
    print("=" * 70)
    print("ARTICLE DISCOVERY TEST")
    print("=" * 70)

    discovered = discover_articles(max_per_source=3, total_limit=10)

    print("\n" + "=" * 70)
    print("DISCOVERED ARTICLES:")
    print("=" * 70)

    for i, article in enumerate(discovered, 1):
        print(f"\n{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   URL: {article.url}")
        print(f"   Published: {article.published}")
        print(f"   Summary: {article.summary[:150]}...")

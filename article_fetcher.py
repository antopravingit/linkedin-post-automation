"""
Article fetcher - Fetches and extracts article content from URLs.
Uses newspaper3k for reliable content extraction.
"""

import newspaper
from typing import Optional, Dict
from dataclasses import dataclass


@dataclass
class Article:
    """Data class for article information."""
    title: str
    url: str
    content: str
    authors: list
    publish_date: Optional[str]
    top_image: Optional[str]
    text: str

    def word_count(self) -> int:
        """Return the word count of the article text."""
        return len(self.text.split())


def fetch_article(url: str, title_override: Optional[str] = None) -> Optional[Article]:
    """
    Fetch and extract article content from a URL.

    Args:
        url: The URL of the article to fetch
        title_override: Optional title to use instead of extracted one

    Returns:
        Article object with content and metadata, or None if fetch fails
    """
    try:
        # Configure newspaper Article
        article = newspaper.Article(url, fetch_images=False)
        article.download()
        article.parse()

        # Check if we got meaningful content
        if not article.text or len(article.text.strip()) < 50:
            print(f"[!] Warning: Could not extract meaningful content from: {url}")
            return None

        # Use provided title or extracted title
        title = title_override if title_override else article.title

        return Article(
            title=title or "Untitled",
            url=url,
            content=article.text,
            authors=article.authors,
            publish_date=str(article.publish_date) if article.publish_date else None,
            top_image=article.top_image if article.top_image else None,
            text=article.text
        )

    except Exception as e:
        print(f"[!] Warning: Failed to fetch article from {url}")
        print(f"  Error: {str(e)}")
        return None


def fetch_multiple_articles(article_inputs: list[tuple[str, str]]) -> list[Article]:
    """
    Fetch multiple articles from a list of (title, url) tuples.
    Title can be None - will be auto-fetched from the article.

    Args:
        article_inputs: List of (title, url) tuples where title can be None

    Returns:
        List of successfully fetched Article objects
    """
    articles = []

    for title, url in article_inputs:
        # Show better message when title is not provided
        if title:
            print(f"\nFetching: {title}")
        else:
            print(f"\nFetching article...")

        print(f"URL: {url}")

        article = fetch_article(url, title_override=title)

        if article:
            articles.append(article)
            # Show the fetched title
            if not title:
                print(f"    Title: {article.title}")
            print(f"[+] Successfully fetched ({article.word_count()} words)")
        else:
            print(f"[X] Skipped (fetch failed or no content)")

    return articles

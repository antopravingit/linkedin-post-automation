"""
Draft generator - Creates LinkedIn post drafts following formatting rules.
"""

import re
from article_fetcher import Article
from article_selector import get_selection_reasoning, score_article


def extract_key_point(text: str, max_chars: int = 200) -> str:
    """
    Extract the most meaningful insight from article text.

    Args:
        text: Full article text
        max_chars: Maximum characters for the excerpt

    Returns:
        Clean, concise key point
    """
    # Remove excessive whitespace and common artifacts
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'Credit:.*?Alamy', '', text)  # Remove photo credits
    text = re.sub(r'^\d+\s*', '', text)  # Remove leading numbers

    # Split into sentences
    sentences = [s.strip() for s in text.split('. ') if s.strip() and len(s.strip()) > 20]

    if not sentences:
        return text[:max_chars].rsplit(' ', 1)[0] + "..." if len(text) > max_chars else text

    # Try to find the most substantial sentence (not too short, not too long)
    for sentence in sentences:
        if 60 < len(sentence) < max_chars:
            return sentence + "."

    # Fallback: use first meaningful sentence
    first = sentences[0]
    if len(first) > max_chars:
        first = first[:max_chars].rsplit(' ', 1)[0] + "..."
    return first + "." if not first.endswith('.') else first


def generate_linkedin_post(article: Article) -> str:
    """
    Generate a LinkedIn post draft from an article.

    Constraints:
    - Human tone, no bot-like language
    - No emojis
    - No hashtags unless valuable (max 2)
    - 3-5 lines ideal (what you see without "see more")
    - Engaging and shareable
    - Optional: include article URL at end

    Args:
        article: Article object

    Returns:
        LinkedIn post draft string
    """
    # Extract key insights from article
    key_point = extract_key_point(article.text, max_chars=200)
    title_lower = article.title.lower()

    # Determine article type and create contextual opening (FIRST-PERSON)
    if any(word in title_lower for word in ["research", "study", "paper", "findings"]):
        opening = "I just read some research that really made me think."
        closing = "What I learned challenges some assumptions about what works in practice."
    elif any(word in title_lower for word in ["open-source", "beats", "outperforms"]):
        opening = "Something I came across today really stuck with me."
        closing = "The open-source ecosystem continues to deliver strong alternatives to proprietary solutions."
    elif any(word in title_lower for word in ["report", "index", "survey", "data"]):
        opening = "I've been looking at some data that caught my attention."
        closing = "Hard numbers help cut through the noise in fast-moving spaces."
    elif any(word in title_lower for word in ["breakthrough", "advance", "discover"]):
        opening = "I just read about something that could be a game-changer."
        closing = "Progress often comes from unexpected places."
    elif any(word in title_lower for word in ["how", "guide", "tutorial", "best"]):
        opening = "I just came across a practical insight worth sharing."
        closing = "Sometimes the most valuable advances are in better methods, not just new models."
    elif any(word in title_lower for word in ["risk", "challenge", "problem", "concern"]):
        opening = "I've been thinking about an important consideration."
        closing = "Understanding limitations is just as important as celebrating capabilities."
    else:
        opening = "I just read something that's worth your time."
        closing = "Articles like this help us look beyond the headlines to what's actually happening."

    # Build post (3-5 lines ideal, engaging)
    post_lines = [
        opening,
        "",
        key_point,
        "",
        closing,
        "",
        f"{article.url}"
    ]

    return "\n".join(post_lines)


def generate_approval_pack(articles: list[Article]) -> str:
    """
    Generate the complete approval pack with 5 detailed articles.

    Args:
        articles: List of selected Article objects (will use top 5)

    Returns:
        Complete approval pack as formatted string
    """
    pack_lines = []

    # Limit to top 5 articles (mix of technical and non-technical)
    articles = articles[:5]

    for i, article in enumerate(articles, 1):
        score = score_article(article)
        reasoning = get_selection_reasoning(article, score)

        # Extract summary points from article
        summary_points = generate_summary_points(article)

        pack_lines.append(f"ARTICLE {i}: {article.title}")
        pack_lines.append(f"Article Title: {article.title}")
        pack_lines.append(f"Article URL: {article.url}")
        pack_lines.append("")
        pack_lines.append("ARTICLE SUMMARY:")
        for point in summary_points:
            pack_lines.append(f"{point}")
        pack_lines.append("")
        pack_lines.append("WHY THIS MATTERS:")
        pack_lines.append(reasoning)
        pack_lines.append("")
        pack_lines.append("LINKEDIN POST:")
        pack_lines.append("")

        post = generate_linkedin_post(article)
        pack_lines.append(post)

        # Add separator if more articles
        if i < len(articles):
            pack_lines.append("")
            pack_lines.append("=" * 70)
            pack_lines.append("")

    return "\n".join(pack_lines)


def generate_summary_points(article: Article) -> list[str]:
    """
    Generate 4-6 bullet points summarizing the article.

    Args:
        article: Article object

    Returns:
        List of summary bullet points
    """
    points = []

    # First bullet: what the article is about
    points.append(f"[Article about {article.title[:50]}...]")

    # Extract key themes from article text
    text_lower = article.text.lower()

    # Look for specific themes
    if "research" in text_lower or "study" in text_lower:
        points.append("[• Research-based analysis with data and findings]")
    if "ai" in text_lower or "machine learning" in text_lower:
        points.append("[• Focuses on AI/ML applications and implications]")
    if "open source" in text_lower or "open-source" in text_lower:
        points.append("[• Discusses open-source developments]")
    if "model" in text_lower:
        points.append("[• Covers model capabilities or limitations]")
    if "method" in text_lower or "approach" in text_lower:
        points.append("[• Proposes methods or approaches]")
    if "challenge" in text_lower or "problem" in text_lower:
        points.append("[• Addresses key challenges in the field]")

    # Add generic point if needed
    if len(points) < 4:
        points.append("[• Provides practical insights for professionals]")

    # Ensure we have 4-6 points
    while len(points) < 4:
        points.append("[• Additional context in full article]")

    return points[:6]  # Max 6 points


def save_approval_pack(pack_content: str) -> str:
    """
    Save approval pack to a timestamped markdown file.

    Args:
        pack_content: The formatted approval pack content

    Returns:
        Path to the saved file
    """
    from datetime import datetime
    import os

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"approval_pack_{timestamp}.md"

    # Save to current directory
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(pack_content)

    return filepath

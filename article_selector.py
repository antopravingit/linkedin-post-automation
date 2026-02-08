"""
Article selector - Scores and selects the best articles based on
substance, originality, and professional value.
"""

from typing import List
from article_fetcher import Article


# Clickbait patterns to identify and downweight
CLICKBAIT_PATTERNS = [
    "you won't believe",
    "shocking",
    "mind-blowing",
    "will change everything",
    "this will blow your mind",
    "scientists hate",
    "one weird trick",
    "must read",
    "unbelievable",
    "incredible",
    "amazing",
    "revolutionary",
]

# Keywords that indicate substantive, professional content
PROFESSIONAL_KEYWORDS = [
    # Proven implementations (highest priority)
    "implementation",
    "deployment",
    "production",
    "real-world",
    "case study",
    "success story",
    "proven",
    "tested",
    "validated",
    "worked",
    "achieving",
    # Tools and frameworks (Semantic Kernel, etc.)
    "semantic kernel",
    "langchain",
    "hugging face",
    "openai",
    "anthropic",
    "pytorch",
    "tensorflow",
    "api",
    "platform",
    "tool",
    "library",
    "framework",
    # Research and evidence
    "research",
    "study",
    "paper",
    "analysis",
    "breakthrough",
    "findings",
    "data",
    "experiment",
    "algorithm",
    "model",
    "methodology",
    "results",
    "conclusion",
    "published",
    "journal",
    "conference",
    # Technical depth
    "technical",
    "engineering",
    "development",
    "architecture",
    "scalability",
    "optimization",
    "code",
    "tutorial",
    "guide",
    "how to",
]

# Generic/hype topics to avoid
GENERIC_TOPICS = [
    "ai will replace",
    "ai taking over",
    "future of work",
    "ai revolution",
    "ai is here",
]


def score_article(article: Article) -> float:
    """
    Score an article based on substance, originality, and professional value.

    Args:
        article: Article object to score

    Returns:
        Numeric score (higher is better)
    """
    score = 0.0

    # 1. Substance: Prefer longer, meaningful content (boosted for technical depth)
    word_count = article.word_count()

    if word_count < 200:
        score -= 20  # Too short, likely clickbait or summary
    elif word_count < 500:
        score += 10  # Decent length
    elif word_count < 1000:
        score += 40  # Good substantive content (boosted)
    elif word_count < 1500:
        score += 60  # Deep dive article (highly valued)
    else:
        score += 80  # Very long, comprehensive article (top tier)

    # 2. Research institutions and sources (MAJOR BOOST)
    title_text = (article.title + " " + article.text).lower()
    research_institutions = [
        "mit", "stanford", "caltech", "carnegie mellon", "harvard",
        "berkeley", "oxford", "cambridge", "eth zurich", "university",
        "institute", "laboratory", "research lab", "researchers"
    ]
    institution_hits = sum(1 for inst in research_institutions if inst in title_text)
    score += institution_hits * 15  # Big boost for research institutions

    # 3. Specific frameworks and systems (HIGH PRIORITY)
    specific_frameworks = [
        "framework", "architecture", "system", "platform",
        "probabilistic", "nondeterminism", "encompass",
        "transformer", "attention mechanism", "neural architecture",
        "multi-agent", "agent framework", "orchestration"
    ]
    framework_hits = sum(1 for fw in specific_frameworks if fw in title_text)
    score += framework_hits * 10  # Major boost for specific frameworks

    # 4. Professional value: Check for substantive keywords
    professional_hits = sum(1 for kw in PROFESSIONAL_KEYWORDS if kw in title_text)
    score += professional_hits * 3

    # 5. Code/implementation details (HIGH PRIORITY)
    implementation_keywords = [
        "deployment", "production", "real-world", "case study",
        "code", "algorithm", "implementation", "scalability",
        "optimization", "performance", "evaluation", "benchmark",
        "tested", "validated", "proven", "results", "data"
    ]
    impl_hits = sum(1 for kw in implementation_keywords if kw in title_text)
    score += impl_hits * 5

    # 3. Clickbait detection: Penalize common clickbait patterns
    title_lower = article.title.lower()
    clickbait_hits = sum(1 for pattern in CLICKBAIT_PATTERNS if pattern in title_lower)
    score -= clickbait_hits * 15

    # 4. Generic topic detection: Penalize repetitive generic themes
    generic_hits = sum(1 for topic in GENERIC_TOPICS if topic in title_lower)
    score -= generic_hits * 10

    # 5. Title quality: Prefer descriptive, specific titles
    # Penalize all caps, excessive punctuation
    if title_lower.isupper():
        score -= 15
    if "!!!" in article.title:
        score -= 10

    # Bonus for numbers in title (often indicates structured content)
    if any(char.isdigit() for char in article.title):
        score += 5

    return score


def categorize_article(article: Article) -> str:
    """
    Categorize article as 'technical' or 'general'.

    Args:
        article: Article object

    Returns:
        'technical' for implementation/technical content, 'general' otherwise
    """
    text = (article.title + " " + article.text).lower()

    # Technical indicators
    technical_indicators = [
        # Frameworks and systems
        "framework", "architecture", "implementation", "deployment",
        "code", "algorithm", "api", "programming", "software",
        # Technical terms
        "scalability", "optimization", "performance", "benchmark",
        "validation", "testing", "debug", "infrastructure",
        # Data science/ML
        "model", "training", "dataset", "neural", "transformer",
        "pytorch", "tensorflow", "keras", "scikit", "pandas",
        # Research
        "research", "study", "paper", "experiment", "mit", "stanford",
        # Specific frameworks
        "langchain", "hugging face", "semantic kernel", "encompass",
        "probabilistic", "nondeterminism"
    ]

    # Count technical indicators
    tech_score = sum(1 for indicator in technical_indicators if indicator in text)

    # Also check word count - technical articles tend to be longer
    word_count = article.word_count()

    # If it has high technical density or is long/substantive, categorize as technical
    if tech_score >= 3 or (tech_score >= 1 and word_count > 800):
        return "technical"
    else:
        return "general"


def select_best_articles(articles: List[Article], max_options: int = 5) -> List[Article]:
    """
    Select and rank the best articles from a list.

    Args:
        articles: List of Article objects
        max_options: Maximum number of top articles to return (default: 5)

    Returns:
        List of top articles (ranked, up to max_options)
    """
    if not articles:
        return []

    # Score all articles
    scored_articles = [(article, score_article(article)) for article in articles]

    # Sort by score (highest first)
    scored_articles.sort(key=lambda x: x[1], reverse=True)

    # Filter out articles with very low scores (likely poor quality)
    min_score_threshold = -20
    qualified = [(a, s) for a, s in scored_articles if s >= min_score_threshold]

    if not qualified:
        # If all articles scored poorly, return the best one anyway
        qualified = [scored_articles[0]]

    # Return top articles (up to max_options)
    top_articles = [article for article, score in qualified[:max_options]]

    return top_articles


def get_selection_reasoning(article: Article, score: float) -> str:
    """
    Generate a brief explanation of why an article was selected.

    Args:
        article: The selected Article
        score: The calculated score

    Returns:
        Brief explanation string
    """
    reasons = []

    word_count = article.word_count()
    if word_count > 800:
        reasons.append(f"substantive content ({word_count} words)")
    elif word_count > 400:
        reasons.append("good depth")

    text_to_check = (article.title + " " + article.text).lower()
    prof_keywords = [kw for kw in PROFESSIONAL_KEYWORDS if kw in text_to_check]
    if prof_keywords:
        reasons.append(f"professional focus ({prof_keywords[0]})")

    return "Selected for " + ", ".join(reasons) if reasons else "Selected as best available option"

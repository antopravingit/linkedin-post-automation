"""
AI Generator - Uses Claude or OpenAI API to generate contextual LinkedIn posts.
Falls back to template-based generation if no API key is configured.
"""

import os
from typing import Optional, Literal
from article_fetcher import Article


def get_api_provider() -> Optional[Literal["claude", "openai"]]:
    """
    Determine which API provider to use based on environment variables.

    Returns:
        "claude" if ANTHROPIC_API_KEY is set
        "openai" if OPENAI_API_KEY is set
        None if neither is set
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude"
    elif os.getenv("OPENAI_API_KEY"):
        return "openai"
    return None


def generate_with_claude(articles: list[Article]) -> str:
    """
    Generate approval pack using Claude API.

    Args:
        articles: List of fetched Article objects

    Returns:
        Approval pack as formatted string
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    # Prepare article summaries for Claude
    articles_text = ""
    for i, article in enumerate(articles, 1):
        # Truncate article text if too long (Claude has token limits)
        text_preview = article.text[:3000] + "..." if len(article.text) > 3000 else article.text
        articles_text += f"""
ARTICLE {i}:
Title: {article.title}
URL: {article.url}
Word count: {article.word_count()}

Content preview:
{text_preview}

---
"""

    system_prompt = """You are an expert AI content curator for LinkedIn. Your task is to analyze AI-related articles and generate approval packs with multiple post options.

CRITICAL REQUIREMENT: You MUST select and generate approval packs for EXACTLY 5 articles total.
Include a mix of technical and non-technical articles for variety (aim for 2-3 technical, 2-3 general/non-technical).

SELECTION RULES:
- Prefer substance over hype
- Prefer original sources over reposts
- Avoid repetitive topics (e.g., generic "AI will change everything")
- Choose something that adds insight for professionals
- Select exactly 5 articles total (mix of technical and general/non-technical)

LINKEDIN POST RULES:
- Sound like a real person, not a news bot
- No emojis
- No hashtags unless they add real value (max 2)
- Avoid marketing language
- Professional and clear tone
- Length: 3-10 lines depending on content value (not rigid)
  * Quick news: 3-5 lines
  * In-depth insights: 6-10 lines if content is truly valuable
- Engaging hook to grab attention
- Key insight or takeaway
- Include specific details and context
- IMPORTANT: MUST include the actual article URL at the end (use the exact URL provided in the article data above)
- Write as if you're sharing something valuable with your network
- Make it worth reading regardless of length

OUTPUT FORMAT (STRICT):
You MUST produce exactly 5 articles total. Number them ARTICLE 1 through ARTICLE 5.
For each selected article, produce:

ARTICLE [Number]: [Article Title]
Article Title: [exact title]
Article URL: [exact URL]

ARTICLE SUMMARY:
[4-6 detailed bullet points explaining what the article is about]
• Point 1
• Point 2
• Point 3
• Point 4

WHY THIS MATTERS:
[2-3 sentences explaining the significance and professional value]

LINKEDIN POST:
[A concise 3-5 line LinkedIn post that includes:
- Engaging hook or opening
- Key insight from the article (1-2 lines)
- Why it matters or takeaway (1 line)
- REQUIRED: The actual article URL at the end (use the exact URL from the article data provided above)]
- Keep it under the "see more" cutoff for maximum engagement]

[Repeat for ARTICLE 2, ARTICLE 3, ARTICLE 4, and ARTICLE 5 - all 5 articles are REQUIRED]

IMPORTANT:
- Do NOT mention AI, models, or how you selected the article
- Do NOT invent facts, quotes, or claims - only use information from the article
- Verify all claims against the provided article content
- If unsure about a fact, omit it rather than guess
- Do NOT exaggerate or hype up the content
- The ARTICLE SUMMARY and WHY THIS MATTERS are for the user's understanding
- The LINKEDIN POST is what actually gets posted
- Make each post unique, insightful, and professional
- You MUST generate exactly 5 articles - no more, no less
"""

    user_message = f"""MUST SELECT EXACTLY 5 ARTICLES FROM THESE {len(articles)} ARTICLES.

REQUIREMENT: Generate approval packs for ALL 5 articles - no more, no less.

ARTICLE MIX (select exactly 5 total):
- Aim for 2-3 TECHNICAL articles: Proven AI implementations, frameworks, deployments, case studies, research papers
- Aim for 2-3 GENERAL/NON-TECHNICAL articles: Business impact, trends, ethics, strategy, workforce changes

SELECTION STRATEGY:
- Choose the 5 BEST articles overall (mix of technical and general)
- Ensure variety in topics and approaches
- Balance between quick news (3-5 lines) and in-depth insights (6-10 lines)

RANK BY:
1. Practical value (proven implementations for technical, business impact for general)
2. Relevance to professionals
3. Specificity (concrete details over vague promises)
4. Evidence (data, case studies, real examples)
5. Actionability (can readers apply this?)
6. Freshness (recent developments and news)

{articles_text}

CRITICAL REMINDER: You MUST generate approval packs for ALL 5 articles.
Number them clearly as ARTICLE 1, ARTICLE 2, ARTICLE 3, ARTICLE 4, ARTICLE 5.
For each article, provide the full summary and LinkedIn post as specified.
Do NOT stop at 3 articles - all 5 are required."""

    print("\n[AI] Generating approval pack with Claude API...")
    print(f"[AI] Processing {len(articles)} article(s)...")

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=6000,  # Increased to accommodate 10 articles
        temperature=0.7,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    approval_pack = message.content[0].text

    # Validate that we got 5 articles
    article_count = approval_pack.count("ARTICLE ")
    if article_count < 5:
        print(f"[!] WARNING: AI only generated {article_count} articles instead of 5.")
        print(f"[!] The prompt instructions were not followed properly.")
        print(f"[!] You may need to re-run or adjust the prompt.")

    print(f"[AI] Approval pack generated successfully ({article_count} articles).")
    return approval_pack


def generate_with_openai(articles: list[Article]) -> str:
    """
    Generate approval pack using OpenAI API.

    Args:
        articles: List of fetched Article objects

    Returns:
        Approval pack as formatted string
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    # Prepare article summaries for GPT
    articles_text = ""
    for i, article in enumerate(articles, 1):
        # Truncate article text if too long
        text_preview = article.text[:3000] + "..." if len(article.text) > 3000 else article.text
        articles_text += f"""
ARTICLE {i}:
Title: {article.title}
URL: {article.url}
Word count: {article.word_count()}

Content preview:
{text_preview}

---
"""

    system_prompt = """You are an expert AI content curator for LinkedIn. Your task is to analyze AI-related articles and generate approval packs with multiple post options.

CRITICAL REQUIREMENT: You MUST select and generate approval packs for EXACTLY 5 articles total.
Include a mix of technical and non-technical articles for variety (aim for 2-3 technical, 2-3 general/non-technical).

SELECTION RULES:
- Prefer substance over hype
- Prefer original sources over reposts
- Avoid repetitive topics (e.g., generic "AI will change everything")
- Choose something that adds insight for professionals
- Select exactly 5 articles total (mix of technical and general/non-technical)

LINKEDIN POST RULES:
- Sound like a real person, not a news bot
- No emojis
- No hashtags unless they add real value (max 2)
- Avoid marketing language
- Professional and clear tone
- Length: 3-10 lines depending on content value (not rigid)
  * Quick news: 3-5 lines
  * In-depth insights: 6-10 lines if content is truly valuable
- Engaging hook to grab attention
- Key insight or takeaway
- Include specific details and context
- IMPORTANT: MUST include the actual article URL at the end (use the exact URL provided in the article data above)
- Write as if you're sharing something valuable with your network
- Make it worth reading regardless of length

OUTPUT FORMAT (STRICT):
You MUST produce exactly 5 articles total. Number them ARTICLE 1 through ARTICLE 5.
For each selected article, produce:

ARTICLE [Number]: [Article Title]
Article Title: [exact title]
Article URL: [exact URL]

ARTICLE SUMMARY:
[4-6 detailed bullet points explaining what the article is about]
• Point 1
• Point 2
• Point 3
• Point 4

WHY THIS MATTERS:
[2-3 sentences explaining the significance and professional value]

LINKEDIN POST:
[A concise 3-5 line LinkedIn post that includes:
- Engaging hook or opening
- Key insight from the article (1-2 lines)
- Why it matters or takeaway (1 line)
- REQUIRED: The actual article URL at the end (use the exact URL from the article data provided above)]
- Keep it under the "see more" cutoff for maximum engagement]

[Repeat for ARTICLE 2, ARTICLE 3, ARTICLE 4, and ARTICLE 5 - all 5 articles are REQUIRED]

IMPORTANT:
- Do NOT mention AI, models, or how you selected the article
- Do NOT invent facts, quotes, or claims - only use information from the article
- Verify all claims against the provided article content
- If unsure about a fact, omit it rather than guess
- Do NOT exaggerate or hype up the content
- The ARTICLE SUMMARY and WHY THIS MATTERS are for the user's understanding
- The LINKEDIN POST is what actually gets posted
- Make each post unique, insightful, and professional
- You MUST generate exactly 5 articles - no more, no less
"""

    user_message = f"""MUST SELECT EXACTLY 5 ARTICLES FROM THESE {len(articles)} ARTICLES.

REQUIREMENT: Generate approval packs for ALL 5 articles - no more, no less.

ARTICLE MIX (select exactly 5 total):
- Aim for 2-3 TECHNICAL articles: Proven AI implementations, frameworks, deployments, case studies, research papers
- Aim for 2-3 GENERAL/NON-TECHNICAL articles: Business impact, trends, ethics, strategy, workforce changes

SELECTION STRATEGY:
- Choose the 5 BEST articles overall (mix of technical and general)
- Ensure variety in topics and approaches
- Balance between quick news (3-5 lines) and in-depth insights (6-10 lines)

RANK BY:
1. Practical value (proven implementations for technical, business impact for general)
2. Relevance to professionals
3. Specificity (concrete details over vague promises)
4. Evidence (data, case studies, real examples)
5. Actionability (can readers apply this?)
6. Freshness (recent developments and news)

{articles_text}

CRITICAL REMINDER: You MUST generate approval packs for ALL 5 articles.
Number them clearly as ARTICLE 1, ARTICLE 2, ARTICLE 3, ARTICLE 4, ARTICLE 5.
For each article, provide the full summary and LinkedIn post as specified.
Do NOT stop at 3 articles - all 5 are required."""

    print("\n[AI] Generating approval pack with OpenAI API...")
    print(f"[AI] Processing {len(articles)} article(s)...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=6000,  # Increased to accommodate 10 articles
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    approval_pack = response.choices[0].message.content

    # Validate that we got 10 articles
    article_count = approval_pack.count("ARTICLE ")
    if article_count < 10:
        print(f"[!] WARNING: AI only generated {article_count} articles instead of 10.")
        print(f"[!] The prompt instructions were not followed properly.")
        print(f"[!] You may need to re-run or adjust the prompt.")

    print(f"[AI] Approval pack generated successfully ({article_count} articles).")
    return approval_pack


def generate_approval_pack_ai(articles: list[Article]) -> tuple[str, str]:
    """
    Generate approval pack using AI API (Claude or OpenAI).

    Args:
        articles: List of fetched Article objects

    Returns:
        Tuple of (approval_pack_text, provider_used)

    Raises:
        ValueError: If no API key is configured
    """
    provider = get_api_provider()

    if provider == "claude":
        return generate_with_claude(articles), "Claude"
    elif provider == "openai":
        return generate_with_openai(articles), "OpenAI"
    else:
        raise ValueError(
            "No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY "
            "environment variable to use AI generation, or the tool will "
            "fall back to template-based generation."
        )

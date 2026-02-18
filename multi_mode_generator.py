#!/usr/bin/env python3
"""
Multi-Mode Generator - Generates LinkedIn posts from various content sources.

Supports 4 content types:
1. Personal Experience (your own learnings)
2. Learned from Colleagues/Team (insights from others)
3. Technology Deep Dives (your technical perspective)
4. Community Insights (meetups, conferences, discussions)
"""

import os
from typing import Optional
from datetime import datetime


def generate_colleague_insight_with_claude(
    colleague_name: str,
    topic: str,
    what_you_learned: str,
    your_experience: str = ""
) -> str:
    """
    Generate a post about insights learned from a colleague using Claude API.

    Args:
        colleague_name: Name of the colleague
        topic: What the insight was about
        what_you_learned: 1-2 sentences describing what they taught you
        your_experience: Optional context about your experience level

    Returns:
        Formatted LinkedIn post
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    from prompts import COLLEAGUE_INSIGHT_PROMPT

    user_message = f"""Write a LinkedIn post about an insight I learned from my colleague.

COLLEAGUE: {colleague_name}
TOPIC: {topic}
WHAT I LEARNED: {what_you_learned}
MY EXPERIENCE: {your_experience if your_experience else "Not specified"}

Write an authentic, first-person post that:
- Mentions {colleague_name} naturally
- Shares what they taught me about {topic}
- Explains why this insight is valuable
- Sounds genuine and appreciative
- Shows growth mindset
- 3-10 lines, professional but conversational
"""

    print(f"\n[AI] Generating colleague insight post with Claude API...")
    print(f"[AI] Colleague: {colleague_name}")
    print(f"[AI] Topic: {topic}")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=0.8,
        system=COLLEAGUE_INSIGHT_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    post = response.content[0].text.strip()

    # Format as approval pack
    formatted = format_colleague_insight_pack(post, colleague_name, topic)

    print(f"[AI] Colleague insight post generated successfully.")
    return formatted


def generate_colleague_insight_with_openai(
    colleague_name: str,
    topic: str,
    what_you_learned: str,
    your_experience: str = ""
) -> str:
    """Generate colleague insight using OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    from prompts import COLLEAGUE_INSIGHT_PROMPT

    user_message = f"""Write a LinkedIn post about an insight I learned from my colleague.

COLLEAGUE: {colleague_name}
TOPIC: {topic}
WHAT I LEARNED: {what_you_learned}
MY EXPERIENCE: {your_experience if your_experience else "Not specified"}

Write an authentic, first-person post that:
- Mentions {colleague_name} naturally
- Shares what they taught me about {topic}
- Explains why this insight is valuable
- Sounds genuine and appreciative
- Shows growth mindset
- 3-10 lines, professional but conversational
"""

    print(f"\n[AI] Generating colleague insight post with OpenAI API...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        temperature=0.8,
        messages=[
            {"role": "system", "content": COLLEAGUE_INSIGHT_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    post = response.choices[0].message.content.strip()
    formatted = format_colleague_insight_pack(post, colleague_name, topic)

    print(f"[AI] Colleague insight post generated successfully.")
    return formatted


def generate_tech_perspective_with_claude(
    technology: str,
    experience_level: str,
    perspective_focus: str,
    specific_insights: str = ""
) -> str:
    """
    Generate a technical perspective post using Claude API.

    Args:
        technology: The technology/tool/framework
        experience_level: Your experience (e.g., "6 months in production", "1 year of use")
        perspective_focus: What perspective to share (e.g., "what papers don't tell you", "production realities")
        specific_insights: Optional specific points to include

    Returns:
        Formatted LinkedIn post
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    from prompts import TECH_PERSPECTIVE_PROMPT

    user_message = f"""Write a LinkedIn technical perspective post.

TECHNOLOGY: {technology}
MY EXPERIENCE: {experience_level}
PERSPECTIVE: {perspective_focus}
SPECIFIC INSIGHTS: {specific_insights if specific_insights else "Not specified"}

Write an authentic, technical post that:
- Establishes my experience level with {technology}
- Shares specific technical insights (not generic advice)
- Includes practical details and real challenges
- Honest assessment of what works/doesn't work
- Actionable advice for others
- 6-12 lines to allow technical depth
- Demonstrates real experience, not just research
"""

    print(f"\n[AI] Generating tech perspective post with Claude API...")
    print(f"[AI] Technology: {technology}")
    print(f"[AI] Experience: {experience_level}")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=3000,
        temperature=0.8,
        system=TECH_PERSPECTIVE_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    post = response.content[0].text.strip()
    formatted = format_tech_perspective_pack(post, technology, perspective_focus)

    print(f"[AI] Tech perspective post generated successfully.")
    return formatted


def generate_tech_perspective_with_openai(
    technology: str,
    experience_level: str,
    perspective_focus: str,
    specific_insights: str = ""
) -> str:
    """Generate tech perspective using OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    from prompts import TECH_PERSPECTIVE_PROMPT

    user_message = f"""Write a LinkedIn technical perspective post.

TECHNOLOGY: {technology}
MY EXPERIENCE: {experience_level}
PERSPECTIVE: {perspective_focus}
SPECIFIC INSIGHTS: {specific_insights if specific_insights else "Not specified"}

Write an authentic, technical post that:
- Establishes my experience level with {technology}
- Shares specific technical insights (not generic advice)
- Includes practical details and real challenges
- Honest assessment of what works/doesn't work
- Actionable advice for others
- 6-12 lines to allow technical depth
"""

    print(f"\n[AI] Generating tech perspective post with OpenAI API...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=3000,
        temperature=0.8,
        messages=[
            {"role": "system", "content": TECH_PERSPECTIVE_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    post = response.choices[0].message.content.strip()
    formatted = format_tech_perspective_pack(post, technology, perspective_focus)

    print(f"[AI] Tech perspective post generated successfully.")
    return formatted


def generate_community_insight_with_claude(
    event: str,
    topic: str,
    what_you_heard: str,
    your_context: str = ""
) -> str:
    """
    Generate a community insight post using Claude API.

    Args:
        event: Type of event (meetup, conference, discussion group, etc.)
        topic: What the insight was about
        what_you_heard: 1-2 sentences describing what you learned
        your_context: Optional context about your connection to the topic

    Returns:
        Formatted LinkedIn post
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    from prompts import COMMUNITY_INSIGHT_PROMPT

    user_message = f"""Write a LinkedIn post about a community insight.

EVENT: {event}
TOPIC: {topic}
WHAT I HEARD: {what_you_heard}
MY CONTEXT: {your_context if your_context else "Not specified"}

Write an authentic post that:
- Mentions the {event} naturally
- Shares what I learned about {topic}
- Explains why this insight stuck with me
- Shows I'm part of a learning community
- Conversational and community-focused
- 3-10 lines
"""

    print(f"\n[AI] Generating community insight post with Claude API...")
    print(f"[AI] Event: {event}")
    print(f"[AI] Topic: {topic}")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=0.8,
        system=COMMUNITY_INSIGHT_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    post = response.content[0].text.strip()
    formatted = format_community_insight_pack(post, event, topic)

    print(f"[AI] Community insight post generated successfully.")
    return formatted


def generate_community_insight_with_openai(
    event: str,
    topic: str,
    what_you_heard: str,
    your_context: str = ""
) -> str:
    """Generate community insight using OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    from prompts import COMMUNITY_INSIGHT_PROMPT

    user_message = f"""Write a LinkedIn post about a community insight.

EVENT: {event}
TOPIC: {topic}
WHAT I HEARD: {what_you_heard}
MY CONTEXT: {your_context if your_context else "Not specified"}

Write an authentic post that:
- Mentions the {event} naturally
- Shares what I learned about {topic}
- Explains why this insight stuck with me
- Shows I'm part of a learning community
- Conversational and community-focused
- 3-10 lines
"""

    print(f"\n[AI] Generating community insight post with OpenAI API...")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=2000,
        temperature=0.8,
        messages=[
            {"role": "system", "content": COMMUNITY_INSIGHT_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    post = response.choices[0].message.content.strip()
    formatted = format_community_insight_pack(post, event, topic)

    print(f"[AI] Community insight post generated successfully.")
    return formatted


# Template-based fallbacks

def generate_template_colleague_insight(
    colleague_name: str,
    topic: str,
    what_you_learned: str
) -> str:
    """Generate colleague insight using templates (AI fallback)."""

    templates = [
        f"My colleague {colleague_name} shared something with me yesterday that really made me think.\n\n{what_you_learned}\n\nThis is why I love working with smart people—they always have a different perspective that teaches me something new.",
        f"Had a great conversation with {colleague_name} today about {topic}.\n\n{what_you_learned}\n\nWhat struck me is how simple but effective this is. Sometimes the best insights come from casual conversations with teammates.",
        f"{colleague_name} showed me a technique for {topic} that I hadn't considered before.\n\n{what_you_learned}\n\nI'm definitely going to try this. It's amazing how much you can learn from the people around you."
    ]

    import hashlib
    template_index = int(hashlib.md5(f"{colleague_name}{topic}".encode()).hexdigest(), 16) % len(templates)
    post = templates[template_index]

    return format_colleague_insight_pack(post, colleague_name, topic)


def generate_template_tech_perspective(
    technology: str,
    experience_level: str,
    perspective_focus: str
) -> str:
    """Generate tech perspective using templates (AI fallback)."""

    post = f"""I've been working with {technology} {experience_level} now. Here's my {perspective_focus}.

The theory makes it look simple. In practice, there are nuances that most documentation doesn't cover.

What surprised me most: sometimes the straightforward approach works better than the complex one.

If you're implementing {technology}, focus on the fundamentals first. Add complexity only when you can prove it helps.

Sometimes the best learning comes from actual production experience, not just tutorials."""

    return format_tech_perspective_pack(post, technology, perspective_focus)


def generate_template_community_insight(
    event: str,
    topic: str,
    what_you_heard: str
) -> str:
    """Generate community insight using templates (AI fallback)."""

    templates = [
        f"At the {event} yesterday, someone mentioned something about {topic} that really stuck with me.\n\n{what_you_heard}\n\nI tried this today and it actually works. Sometimes the best insights come from community discussions, not formal research.",
        f"Had an interesting discussion at the {event} about {topic}.\n\n{what_you_heard}\n\nThis really made me think. I love how these events bring together different perspectives on the same challenges.",
        f"Someone at the {event} shared a tip about {topic} that I hadn't considered.\n\n{what_you_heard}\n\nThis is why I make time for these events—you always learn something new from the community."
    ]

    import hashlib
    template_index = int(hashlib.md5(f"{event}{topic}".encode()).hexdigest(), 16) % len(templates)
    post = templates[template_index]

    return format_community_insight_pack(post, event, topic)


# Formatting functions

def format_colleague_insight_pack(post: str, colleague_name: str, topic: str) -> str:
    """Format colleague insight as approval pack."""
    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""COLLEAGUE INSIGHT: {topic}
Colleague: {colleague_name}
Generated: {date_str}

LINKEDIN POST:

{post}

{"=" * 70}

APPROVAL INSTRUCTIONS:
1. Review the post above
2. Edit to add more specific details if desired
3. Make sure the tone feels authentic to your relationship
4. Post to LinkedIn when ready
"""


def format_tech_perspective_pack(post: str, technology: str, perspective: str) -> str:
    """Format tech perspective as approval pack."""
    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""TECHNICAL PERSPECTIVE: {technology}
Perspective: {perspective}
Generated: {date_str}

LINKEDIN POST:

{post}

{"=" * 70}

APPROVAL INSTRUCTIONS:
1. Review the post above
2. Add more specific technical details from your experience
3. Include concrete examples or numbers if you have them
4. Make sure it sounds authentic to your experience level
5. Post to LinkedIn when ready
"""


def format_community_insight_pack(post: str, event: str, topic: str) -> str:
    """Format community insight as approval pack."""
    date_str = datetime.now().strftime("%Y-%m-%d")

    return f"""COMMUNITY INSIGHT: {topic}
Event: {event}
Generated: {date_str}

LINKEDIN POST:

{post}

{"=" * 70}

APPROVAL INSTRUCTIONS:
1. Review the post above
2. Edit to add more context about the event
3. Make sure it sounds authentic to your experience
4. Post to LinkedIn when ready
"""


# Collection functions

def collect_colleague_insight_input() -> tuple[str, str, str, str]:
    """Interactively collect colleague insight input."""
    print("\n" + "=" * 60)
    print("COLLEAGUE INSIGHT MODE")
    print("=" * 60)
    print("\nShare something you learned from a colleague or team member.")
    print("\nExamples:")
    print("  - Sarah showed me a prompt engineering technique")
    print("  - My lead taught me about database optimization")
    print("  - Our intern asked a question that made me think")
    print()

    colleague_name = input("Colleague's name: ").strip()
    if not colleague_name:
        print("[!] Name is required")
        return collect_colleague_insight_input()

    topic = input("What was the topic? (e.g., 'LLM hallucinations', 'database indexing'): ").strip()
    if not topic:
        print("[!] Topic is required")
        return collect_colleague_insight_input()

    print("\nWhat did you learn from them? (1-2 sentences)")
    what_you_learned = input("Your answer: ").strip()
    if not what_you_learned:
        print("[!] Please describe what you learned")
        return collect_colleague_insight_input()

    print("\n[Optional] Your experience level with this topic (press Enter to skip):")
    your_experience = input("Your experience: ").strip()

    return colleague_name, topic, what_you_learned, your_experience


def collect_tech_perspective_input() -> tuple[str, str, str, str]:
    """Interactively collect tech perspective input."""
    print("\n" + "=" * 60)
    print("TECHNICAL PERSPECTIVE MODE")
    print("=" * 60)
    print("\nShare your technical perspective based on real experience.")
    print("\nExamples:")
    print("  - RAG systems: 'what papers don't tell you'")
    print("  - LangChain: '6 months production experience'")
    print("  - Vector databases: 'Pinecone vs Weaviate comparison'")
    print()

    technology = input("Technology/tool/framework: ").strip()
    if not technology:
        print("[!] Technology is required")
        return collect_tech_perspective_input()

    experience_level = input("Your experience (e.g., '6 months in production'): ").strip()
    if not experience_level:
        print("[!] Experience level is required")
        return collect_tech_perspective_input()

    perspective_focus = input("Your perspective (e.g., 'what papers don't tell you'): ").strip()
    if not perspective_focus:
        print("[!] Perspective focus is required")
        return collect_tech_perspective_input()

    print("\n[Optional] Specific insights to include (press Enter to skip):")
    specific_insights = input("Specific points: ").strip()

    return technology, experience_level, perspective_focus, specific_insights


def collect_community_insight_input() -> tuple[str, str, str, str]:
    """Interactively collect community insight input."""
    print("\n" + "=" * 60)
    print("COMMUNITY INSIGHT MODE")
    print("=" * 60)
    print("\nShare something you learned from a community event.")
    print("\nExamples:")
    print("  - Meetup: 'prompt engineering tips'")
    print("  - Conference: 'new ML technique'")
    print("  - Discussion group: 'deployment challenges'")
    print()

    event = input("Event type (meetup, conference, discussion group, etc.): ").strip()
    if not event:
        print("[!] Event type is required")
        return collect_community_insight_input()

    topic = input("What was the topic? ").strip()
    if not topic:
        print("[!] Topic is required")
        return collect_community_insight_input()

    print("\nWhat did you hear or learn? (1-2 sentences)")
    what_you_heard = input("Your answer: ").strip()
    if not what_you_heard:
        print("[!] Please describe what you learned")
        return collect_community_insight_input()

    print("\n[Optional] Your context or connection to this topic (press Enter to skip):")
    your_context = input("Your context: ").strip()

    return event, topic, what_you_heard, your_context


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    # Test colleague insight
    print("=" * 70)
    print("TEST: COLLEAGUE INSIGHT")
    print("=" * 70)
    name, topic, learned, exp = collect_colleague_insight_input()

    api_provider = os.getenv("ANTHROPIC_API_KEY") and "claude" or (os.getenv("OPENAI_API_KEY") and "openai" or None)

    if api_provider == "claude":
        result = generate_colleague_insight_with_claude(name, topic, learned, exp)
    elif api_provider == "openai":
        result = generate_colleague_insight_with_openai(name, topic, learned, exp)
    else:
        print("[!] AI API required. Using template...")
        result = generate_template_colleague_insight(name, topic, learned)

    print("\n" + result)

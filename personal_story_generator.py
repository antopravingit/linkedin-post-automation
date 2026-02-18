#!/usr/bin/env python3
"""
Personal Story Generator - Generates pure personal experience posts
without requiring articles. Uses AI to craft authentic-sounding stories.
"""

import os
from typing import Optional
from datetime import datetime


def generate_personal_story_with_claude(
    topic: str,
    story_type: str = "professional_learning",
    length: str = "medium"
) -> str:
    """
    Generate a personal experience story using Claude API.

    Args:
        topic: The topic/theme for the personal story
        story_type: Type of story - "professional_learning", "challenge_overcome",
                    "insight_gained", "career_moment"
        length: "short" (3-5 lines), "medium" (6-10 lines), "long" (10-15 lines)

    Returns:
        Formatted personal story post ready for LinkedIn
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    length_guidance = {
        "short": "3-5 lines (quick insight)",
        "medium": "6-10 lines (balanced storytelling)",
        "long": "10-15 lines (deeper reflection)"
    }

    system_prompt = f"""You are an authentic LinkedIn professional sharing a genuine personal experience.

STORY TYPE: {story_type}
LENGTH: {length_guidance.get(length, "6-10 lines")}

CRITICAL RULES:
- Write ENTIRELY in first-person ("I", "my", "me")
- Make it sound like a REAL personal experience (not generated)
- Use specific details and concrete examples
- Include emotions/thoughts/struggles (not just outcomes)
- Avoid generic platitudes and clichés
- No emojis
- Professional but conversational tone
- Length: {length_guidance.get(length, "6-10 lines")}

STORY STRUCTURE:
1. Hook: Start in the middle of the action or with a thought/feeling
2. Context: Briefly set the scene (2-3 sentences)
3. The Experience: What actually happened (main part)
4. The Insight: What you learned or why it matters (1-2 sentences)
5. Takeaway: Optional closing thought

AUTHENTICITY GUIDELINES:
- Include specific details (times, places, numbers, names of frameworks/tools)
- Show vulnerability (admit mistakes, struggles, doubts)
- Use natural language (contractions, occasional incomplete sentences)
- Avoid: "revolutionary", "game-changing", "unbelievable", "amazing"
- Prefer: "interesting", "surprising", "challenging", "worth considering"

Write authentically about: {topic}
"""

    user_message = f"""Write a personal LinkedIn post about: {topic}

Make it sound authentic and specific. Include:
- Concrete details (not vague generalizations)
- Personal thoughts or feelings
- A clear insight or takeaway
- Professional but conversational tone

Write {length} length post."""

    print("\n[AI] Generating personal story with Claude API...")
    print(f"[AI] Topic: {topic}")
    print(f"[AI] Type: {story_type}, Length: {length}")

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0.8,  # Higher for more creativity
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    story = response.content[0].text

    # Format as approval pack
    formatted = format_personal_story_pack(story, topic, story_type)

    print(f"[AI] Personal story generated successfully.")
    return formatted


def generate_personal_story_with_openai(
    topic: str,
    story_type: str = "professional_learning",
    length: str = "medium"
) -> str:
    """
    Generate a personal experience story using OpenAI API.

    Args:
        topic: The topic/theme for the personal story
        story_type: Type of story - "professional_learning", "challenge_overcome",
                    "insight_gained", "career_moment"
        length: "short" (3-5 lines), "medium" (6-10 lines), "long" (10-15 lines)

    Returns:
        Formatted personal story post ready for LinkedIn
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = openai.OpenAI(api_key=api_key)

    length_guidance = {
        "short": "3-5 lines (quick insight)",
        "medium": "6-10 lines (balanced storytelling)",
        "long": "10-15 lines (deeper reflection)"
    }

    system_prompt = f"""You are an authentic LinkedIn professional sharing a genuine personal experience.

STORY TYPE: {story_type}
LENGTH: {length_guidance.get(length, "6-10 lines")}

CRITICAL RULES:
- Write ENTIRELY in first-person ("I", "my", "me")
- Make it sound like a REAL personal experience (not generated)
- Use specific details and concrete examples
- Include emotions/thoughts/struggles (not just outcomes)
- Avoid generic platitudes and clichés
- No emojis
- Professional but conversational tone
- Length: {length_guidance.get(length, "6-10 lines")}

STORY STRUCTURE:
1. Hook: Start in the middle of the action or with a thought/feeling
2. Context: Briefly set the scene (2-3 sentences)
3. The Experience: What actually happened (main part)
4. The Insight: What you learned or why it matters (1-2 sentences)
5. Takeaway: Optional closing thought

AUTHENTICITY GUIDELINES:
- Include specific details (times, places, numbers, names of frameworks/tools)
- Show vulnerability (admit mistakes, struggles, doubts)
- Use natural language (contractions, occasional incomplete sentences)
- Avoid: "revolutionary", "game-changing", "unbelievable", "amazing"
- Prefer: "interesting", "surprising", "challenging", "worth considering"

Write authentically about: {topic}
"""

    user_message = f"""Write a personal LinkedIn post about: {topic}

Make it sound authentic and specific. Include:
- Concrete details (not vague generalizations)
- Personal thoughts or feelings
- A clear insight or takeaway
- Professional but conversational tone

Write {length} length post."""

    print("\n[AI] Generating personal story with OpenAI API...")
    print(f"[AI] Topic: {topic}")
    print(f"[AI] Type: {story_type}, Length: {length}")

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4000,
        temperature=0.8,  # Higher for more creativity
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    story = response.choices[0].message.content

    # Format as approval pack
    formatted = format_personal_story_pack(story, topic, story_type)

    print(f"[AI] Personal story generated successfully.")
    return formatted


def format_personal_story_pack(
    story: str,
    topic: str,
    story_type: str
) -> str:
    """Format a personal story as an approval pack."""
    date_str = datetime.now().strftime("%Y-%m-%d")

    pack_lines = [
        f"PERSONAL STORY: {topic}",
        f"Story Type: {story_type}",
        f"Generated: {date_str}",
        "",
        "STORY CONTEXT:",
        f"This is a pure personal experience story about: {topic}",
        "",
        "LINKEDIN POST:",
        "",
        story,
        "",
        "=" * 70,
        "",
        "APPROVAL INSTRUCTIONS:",
        "1. Review the story above",
        "2. Edit to add personal details if desired",
        "3. Make it more specific to your experience",
        "4. Add specific examples from your work/life",
        "5. Post to LinkedIn when ready"
    ]

    return "\n".join(pack_lines)


def generate_template_personal_story(
    topic: str,
    story_type: str = "professional_learning"
) -> str:
    """
    Generate a personal experience post using templates.

    Args:
        topic: The topic/theme
        story_type: Type of story

    Returns:
        Formatted personal story post
    """
    templates = {
        "professional_learning": [
            "Been thinking about {topic} a lot lately.\n\nWhat I've realized is...\n\n",
            "Something I wish I knew earlier about {topic}:\n\n",
            "Here's what I've learned about {topic} recently:\n\n"
        ],
        "challenge_overcome": [
            "Ran into a challenge with {topic} recently.\n\nHere's how I worked through it:\n\n",
            "Dealing with {topic} wasn't easy, but...\n\n",
            "When I faced {topic}, I had to get creative.\n\n"
        ],
        "insight_gained": [
            "Had an interesting realization about {topic} today.\n\n",
            "Something clicked for me about {topic}:\n\n",
            "New perspective on {topic}:\n\n"
        ],
        "career_moment": [
            "Reflecting on my journey with {topic}.\n\n",
            "Career milestone moment: {topic}\n\n",
            "Looking back at {topic}:\n\n"
        ]
    }

    template_list = templates.get(story_type, templates["professional_learning"])

    # Select template based on topic hash for consistency
    import hashlib
    template_index = int(hashlib.md5(topic.encode()).hexdigest(), 16) % len(template_list)
    template = template_list[template_index]

    # Build the post
    post_lines = [
        template.format(topic=topic),
        f"[Add your specific experience with {topic} here]",
        "",
        f"Main takeaway: [What you learned]",
        "",
        "This matters because [why it's important]",
        "",
        "#ProfessionalDevelopment #Learning"
    ]

    post = "\n".join(post_lines)

    # Format as approval pack
    pack_lines = [
        f"PERSONAL STORY: {topic}",
        f"Story Type: {story_type}",
        "",
        "LINKEDIN POST:",
        "",
        post,
        "",
        "=" * 70,
        "",
        "EDITING INSTRUCTIONS:",
        "1. Replace bracketed text with your specific details",
        "2. Add concrete examples from your experience",
        "3. Make it more personal and specific",
        "4. Remove hashtags if desired"
    ]

    return "\n".join(pack_lines)


def collect_story_topic() -> tuple[str, str, str]:
    """
    Interactively collect story topic from user.

    Returns:
        Tuple of (topic, story_type, length)
    """
    print("\n" + "=" * 60)
    print("PERSONAL STORY MODE")
    print("=" * 60)
    print("\nWhat would you like to write about?")
    print("\nExamples:")
    print("  - A mistake I made and what I learned")
    print("  - Something that changed my mind about AI")
    print("  - A challenge I overcame at work")
    print("  - An insight from a recent project")
    print("  - Something I wish I knew earlier")
    print()

    topic = input("Your topic: ").strip()

    if not topic:
        print("[!] Topic cannot be empty")
        return collect_story_topic()

    print("\nStory Type:")
    print("  1. Professional Learning (something I learned)")
    print("  2. Challenge Overcome (problem I solved)")
    print("  3. Insight Gained (new perspective)")
    print("  4. Career Moment (milestone or reflection)")
    print()

    type_choice = input("Choose type (1-4, default=1): ").strip()

    type_map = {
        "1": "professional_learning",
        "2": "challenge_overcome",
        "3": "insight_gained",
        "4": "career_moment"
    }

    story_type = type_map.get(type_choice, "professional_learning")

    print("\nPost Length:")
    print("  1. Short (3-5 lines)")
    print("  2. Medium (6-10 lines)")
    print("  3. Long (10-15 lines)")
    print()

    length_choice = input("Choose length (1-3, default=2): ").strip()

    length_map = {
        "1": "short",
        "2": "medium",
        "3": "long"
    }

    length = length_map.get(length_choice, "medium")

    return topic, story_type, length


if __name__ == "__main__":
    # Test personal story generation
    from dotenv import load_dotenv
    load_dotenv()

    topic, story_type, length = collect_story_topic()

    api_provider = os.getenv("ANTHROPIC_API_KEY") and "claude" or (os.getenv("OPENAI_API_KEY") and "openai" or None)

    if api_provider == "claude":
        approval_pack = generate_personal_story_with_claude(topic, story_type, length)
    elif api_provider == "openai":
        approval_pack = generate_personal_story_with_openai(topic, story_type, length)
    else:
        print("[!] AI API required for personal story mode")
        print("[*] Using template-based generation...")
        approval_pack = generate_template_personal_story(topic, story_type)

    print("\n" + "=" * 70)
    print("PERSONAL STORY")
    print("=" * 70)
    print()
    print(approval_pack)

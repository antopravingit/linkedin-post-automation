#!/usr/bin/env python3
"""
Interview Generator - AI interviews user to generate authentic posts.

The system asks 2-3 targeted questions and generates a post based on the responses.
This creates more personalized content than fully automated generation.
"""

import os
from typing import Optional


def interview_colleague_insight(colleague_name: str, topic: str) -> str:
    """
    Interview user about colleague insight and generate post.

    Args:
        colleague_name: Name of the colleague
        topic: Topic of the insight

    Returns:
        Generated LinkedIn post
    """
    print("\n" + "=" * 60)
    print("INTERVIEW MODE: Colleague Insight")
    print("=" * 60)
    print(f"\nTell me about what {colleague_name} taught you about {topic}.")
    print("I'll ask a few questions to create an authentic post.\n")

    # Question 1
    print("Question 1 of 3:")
    q1 = input(f"What specific technique or insight did {colleague_name} share? (1-2 sentences)\n> ").strip()

    # Question 2
    print("\nQuestion 2 of 3:")
    q2 = input("How does this compare to what you were doing before?\n> ").strip()

    # Question 3
    print("\nQuestion 3 of 3:")
    q3 = input("Why does this matter to you or your work?\n> ").strip()

    # Generate post using AI
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = """You are an expert at crafting authentic LinkedIn posts from interview responses.

Write a first-person post about learning from a colleague that:
- Sounds natural and conversational
- Mentions the colleague naturally
- Shares the specific insight
- Explains why it matters
- 3-10 lines, professional tone
"""

            user_message = f"""Write a LinkedIn post about an insight I learned from my colleague {colleague_name} about {topic}.

INTERVIEW RESPONSES:
1. What they shared: {q1}
2. How it compares to before: {q2}
3. Why it matters: {q3}

Create an authentic post based on these responses. Use my actual words where possible.
Make it sound genuine and appreciative."""

            print("\n[AI] Generating post from your responses...")

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.8,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            post = response.content[0].text.strip()

            from multi_mode_generator import format_colleague_insight_pack
            result = format_colleague_insight_pack(post, colleague_name, topic)

            print("[+] Post generated successfully!\n")
            return result

    except Exception as e:
        print(f"[!] AI generation failed: {e}")
        print("[*] Creating template-based post...")

        # Fallback to template
        post = f"""My colleague {colleague_name} shared something with me about {topic} that really made me think.

{q1}

{q2}

{q3}

This is why I love working with smart people—they always have a different perspective that teaches me something new."""

        from multi_mode_generator import format_colleague_insight_pack
        result = format_colleague_insight_pack(post, colleague_name, topic)

        return result


def interview_tech_perspective(technology: str) -> str:
    """
    Interview user about tech perspective and generate post.

    Args:
        technology: Technology/tool/framework

    Returns:
        Generated LinkedIn post
    """
    print("\n" + "=" * 60)
    print("INTERVIEW MODE: Technical Perspective")
    print("=" * 60)
    print(f"\nTell me about your experience with {technology}.")
    print("I'll ask a few questions to create an authentic technical post.\n")

    # Question 1
    print("Question 1 of 3:")
    q1 = input(f"How long have you been using {technology}? (e.g., '6 months in production')\n> ").strip()

    # Question 2
    print("\nQuestion 2 of 3:")
    q2 = input(f"What's ONE thing about {technology} that surprised you or that most people get wrong?\n> ").strip()

    # Question 3
    print("\nQuestion 3 of 3:")
    q3 = input("What's your top advice for someone just starting with this?\n> ").strip()

    # Generate post using AI
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = """You are an expert at crafting authentic technical LinkedIn posts from interview responses.

Write a first-person technical post that:
- Establishes real experience (not just research)
- Shares specific insights
- Honest assessment (what works, what doesn't)
- Practical and actionable
- 6-12 lines to allow technical depth
- Sounds earned, not theoretical
"""

            user_message = f"""Write a LinkedIn technical perspective post about {technology}.

INTERVIEW RESPONSES:
1. Experience level: {q1}
2. What surprised me/people get wrong: {q2}
3. Top advice: {q3}

Create an authentic technical post based on these responses. Use my actual words where possible.
Make it sound like I've actually used this technology in production."""

            print("\n[AI] Generating post from your responses...")

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                temperature=0.8,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            post = response.content[0].text.strip()

            from multi_mode_generator import format_tech_perspective_pack
            result = format_tech_perspective_pack(post, technology, "production experience")

            print("[+] Post generated successfully!\n")
            return result

    except Exception as e:
        print(f"[!] AI generation failed: {e}")
        print("[*] Creating template-based post...")

        # Fallback to template
        post = f"""I've been working with {technology} {q1} now. Here's what I've learned that the papers don't tell you.

{q2}

{q3}

If you're implementing {technology}, start with the fundamentals. Add complexity only when you can prove it helps.

Sometimes the best learning comes from actual production experience, not just tutorials."""

        from multi_mode_generator import format_tech_perspective_pack
        result = format_tech_perspective_pack(post, technology, "production experience")

        return result


def interview_community_insight(event: str, topic: str) -> str:
    """
    Interview user about community insight and generate post.

    Args:
        event: Type of event
        topic: Topic of the insight

    Returns:
        Generated LinkedIn post
    """
    print("\n" + "=" * 60)
    print("INTERVIEW MODE: Community Insight")
    print("=" * 60)
    print(f"\nTell me about what you learned at the {event} about {topic}.")
    print("I'll ask a few questions to create an authentic post.\n")

    # Question 1
    print("Question 1 of 3:")
    q1 = input("What specific tip or insight did you hear that stuck with you?\n> ").strip()

    # Question 2
    print("\nQuestion 2 of 3:")
    q2 = input("Did you try this yourself or how do you plan to use it?\n> ").strip()

    # Question 3
    print("\nQuestion 3 of 3:")
    q3 = input("Why was this the most interesting thing you learned?\n> ").strip()

    # Generate post using AI
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = """You are an expert at crafting authentic LinkedIn posts from interview responses.

Write a first-person community-focused post that:
- Mentions the event naturally
- Shares the insight clearly
- Shows community engagement
- Conversational and appreciative
- 3-10 lines
- Sounds like a genuine learning moment
"""

            user_message = f"""Write a LinkedIn post about a community insight from {event}.

TOPIC: {topic}
INTERVIEW RESPONSES:
1. What I heard: {q1}
2. How I'll use it: {q2}
3. Why it mattered: {q3}

Create an authentic community-focused post based on these responses. Use my actual words where possible.
Make it sound like I'm part of a learning community."""

            print("\n[AI] Generating post from your responses...")

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.8,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            post = response.content[0].text.strip()

            from multi_mode_generator import format_community_insight_pack
            result = format_community_insight_pack(post, event, topic)

            print("[+] Post generated successfully!\n")
            return result

    except Exception as e:
        print(f"[!] AI generation failed: {e}")
        print("[*] Creating template-based post...")

        # Fallback to template
        post = f"""At the {event}, someone mentioned something about {topic} that really stuck with me.

{q1}

{q2}

{q3}

Sometimes the best insights come from community discussions, not formal research. This is why I make time for these events."""

        from multi_mode_generator import format_community_insight_pack
        result = format_community_insight_pack(post, event, topic)

        return result


def polish_user_content(draft_content: str, content_type: str = "general") -> str:
    """
    Polish user-provided content to enhance while maintaining their voice.

    Args:
        draft_content: User's draft content
        content_type: Type of content (general, colleague, tech, community)

    Returns:
        Polished LinkedIn post
    """
    print("\n" + "=" * 60)
    print("POLISH MODE")
    print("=" * 60)
    print("\nI'll enhance your content while keeping your voice.\n")

    print("Your draft:")
    print("-" * 60)
    print(draft_content)
    print("-" * 60)
    print()

    # Generate polished version using AI
    try:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = """You are an expert at polishing LinkedIn posts while maintaining the author's authentic voice.

Your job:
1. Fix grammar and spelling
2. Improve flow and readability
3. Suggest better word choices (but don't change meaning)
4. Adjust length for LinkedIn (3-10 lines ideally)
5. Add a strong hook if missing
6. Keep the author's voice and personality intact
7. Don't add information they didn't provide
8. Remove any filler or redundancy

CRITICAL: The result must sound like THE SAME PERSON wrote it, just better.
"""

            user_message = f"""Polish this LinkedIn post for me:

{draft_content}

CONTENT TYPE: {content_type}

Requirements:
- Keep my voice and personality
- Fix grammar and improve flow
- Make it more engaging
- Keep it to 3-10 lines
- Don't add new information
- Don't change my meaning"""

            print("[AI] Polishing your content...")

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.7,  # Lower for polishing to maintain voice
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            polished = response.content[0].text.strip()

            print("\n[+] Polished version:")
            print("=" * 60)
            print(polished)
            print("=" * 60)
            print()

            return polished

    except Exception as e:
        print(f"[!] AI polishing failed: {e}")
        print("[*] Returning original draft\n")
        return draft_content


def interactive_polish_mode():
    """Interactive polish mode where user provides content to polish."""
    print("\n" + "=" * 70)
    print("CONTENT POLISHER")
    print("=" * 70)
    print("\nPaste your draft content and I'll polish it for LinkedIn.")
    print("Type 'DONE' on a line by itself when finished.\n")

    lines = []
    print("Your content (paste below):")
    while True:
        line = input()
        if line.strip() == "DONE":
            break
        lines.append(line)

    draft_content = "\n".join(lines)

    if not draft_content.strip():
        print("[!] No content provided")
        return None

    # Ask for content type
    print("\nContent type:")
    print("  1. General")
    print("  2. Colleague insight")
    print("  3. Technical perspective")
    print("  4. Community insight")

    type_choice = input("Choose type (1-4, default=1): ").strip()

    type_map = {
        "1": "general",
        "2": "colleague",
        "3": "tech",
        "4": "community"
    }

    content_type = type_map.get(type_choice, "general")

    # Polish the content
    result = polish_user_content(draft_content, content_type)

    # Save to file
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"polished_post_{timestamp}.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"\n[+] Polished post saved to: {filename}")

    return result


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("=" * 70)
    print("INTERVIEW GENERATOR - Test")
    print("=" * 70)
    print("\nSelect mode:")
    print("  1. Interview colleague insight")
    print("  2. Interview tech perspective")
    print("  3. Interview community insight")
    print("  4. Polish user content")

    choice = input("\nChoose mode (1-4): ").strip()

    if choice == "1":
        name = input("Colleague name: ").strip()
        topic = input("Topic: ").strip()
        result = interview_colleague_insight(name, topic)
    elif choice == "2":
        tech = input("Technology: ").strip()
        result = interview_tech_perspective(tech)
    elif choice == "3":
        event = input("Event type: ").strip()
        topic = input("Topic: ").strip()
        result = interview_community_insight(event, topic)
    elif choice == "4":
        result = interactive_polish_mode()
    else:
        print("[!] Invalid choice")
        sys.exit(1)

    if result:
        print("\n" + result)

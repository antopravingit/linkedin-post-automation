#!/usr/bin/env python3
"""
LinkedIn AI Content Curator

This tool helps you prepare weekly LinkedIn posts about AI by:
1. Auto-discovering articles from AI news sources (OR paste your own URLs)
2. Fetching and analyzing article content
3. Selecting the most interesting/substantial articles using AI
4. Generating approval packs with 3 different LinkedIn post options
5. Optionally pushing to Notion for approval and auto-posting

You will NOT publish anything directly. This prepares content for human review.

FEATURES:
- Auto-discovery: AI finds interesting articles from news sources
- Multiple options: 3 different post styles (Insightful, Concise, Conversational)
- Detailed summaries: Bullet points + context for each article
- Flexible length: Posts adapt to content (3-12 lines)
- Notion integration: Review, approve, and auto-post to LinkedIn

SUPPORTED GENERATION MODES:
- AI-powered: Uses Claude or OpenAI API for contextual insights
- Template-based: Free, rule-based generation (fallback)
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from article_fetcher import fetch_multiple_articles
from article_selector import select_best_articles
from draft_generator import generate_approval_pack, save_approval_pack
from notion_integration import is_notion_configured, create_notion_page, create_notion_pages_for_articles
from ai_generator import get_api_provider, generate_approval_pack_ai
from article_discovery import discover_and_fetch
from multi_mode_generator import (
    collect_colleague_insight_input,
    collect_tech_perspective_input,
    collect_community_insight_input,
    generate_colleague_insight_with_claude,
    generate_colleague_insight_with_openai,
    generate_template_colleague_insight,
    generate_tech_perspective_with_claude,
    generate_tech_perspective_with_openai,
    generate_template_tech_perspective,
    generate_community_insight_with_claude,
    generate_community_insight_with_openai,
    generate_template_community_insight
)
from personal_story_generator import (
    collect_story_topic,
    generate_personal_story_with_claude,
    generate_personal_story_with_openai,
    generate_template_personal_story
)


def handle_non_article_content(content_type: str, api_provider: str, notion_enabled: bool):
    """
    Handle content types that don't require articles.

    Args:
        content_type: Type of content (colleague_insight, tech_perspective, community_insight, personal_experience)
        api_provider: AI provider (claude, openai, or None)
        notion_enabled: Whether Notion integration is enabled
    """
    approval_pack = None

    if content_type == "colleague_insight":
        print("\n[*] Colleague Insight Mode")
        print("[*] Share something you learned from a colleague or team member")

        # Collect input
        colleague_name, topic, what_you_learned, your_experience = collect_colleague_insight_input()

        print(f"\n[*] Generating post about: {topic}")

        # Generate post
        if api_provider == "claude":
            approval_pack = generate_colleague_insight_with_claude(colleague_name, topic, what_you_learned, your_experience)
            print(f"\n[+] Generated with Claude API")
        elif api_provider == "openai":
            approval_pack = generate_colleague_insight_with_openai(colleague_name, topic, what_you_learned, your_experience)
            print(f"\n[+] Generated with OpenAI API")
        else:
            print("[!] AI Generation: Not configured (using template-based generation)")
            approval_pack = generate_template_colleague_insight(colleague_name, topic, what_you_learned)

    elif content_type == "tech_perspective":
        print("\n[*] Technical Perspective Mode")
        print("[*] Share your technical perspective based on real experience")

        # Collect input
        technology, experience_level, perspective_focus, specific_insights = collect_tech_perspective_input()

        print(f"\n[*] Generating post about: {technology}")

        # Generate post
        if api_provider == "claude":
            approval_pack = generate_tech_perspective_with_claude(technology, experience_level, perspective_focus, specific_insights)
            print(f"\n[+] Generated with Claude API")
        elif api_provider == "openai":
            approval_pack = generate_tech_perspective_with_openai(technology, experience_level, perspective_focus, specific_insights)
            print(f"\n[+] Generated with OpenAI API")
        else:
            print("[!] AI Generation: Not configured (using template-based generation)")
            approval_pack = generate_template_tech_perspective(technology, experience_level, perspective_focus)

    elif content_type == "community_insight":
        print("\n[*] Community Insight Mode")
        print("[*] Share something you learned from a community event")

        # Collect input
        event, topic, what_you_heard, your_context = collect_community_insight_input()

        print(f"\n[*] Generating post about: {topic}")

        # Generate post
        if api_provider == "claude":
            approval_pack = generate_community_insight_with_claude(event, topic, what_you_heard, your_context)
            print(f"\n[+] Generated with Claude API")
        elif api_provider == "openai":
            approval_pack = generate_community_insight_with_openai(event, topic, what_you_heard, your_context)
            print(f"\n[+] Generated with OpenAI API")
        else:
            print("[!] AI Generation: Not configured (using template-based generation)")
            approval_pack = generate_template_community_insight(event, topic, what_you_heard)

    elif content_type == "personal_experience":
        print("\n[*] Personal Experience Mode")
        print("[*] Share your own learning or experience")

        # Collect input
        topic, story_type, length = collect_story_topic()

        print(f"\n[*] Generating personal story about: {topic}")

        # Generate post
        if api_provider == "claude":
            approval_pack = generate_personal_story_with_claude(topic, story_type, length)
            print(f"\n[+] Generated with Claude API")
        elif api_provider == "openai":
            approval_pack = generate_personal_story_with_openai(topic, story_type, length)
            print(f"\n[+] Generated with OpenAI API")
        else:
            print("[!] AI Generation: Not configured (using template-based generation)")
            approval_pack = generate_template_personal_story(topic, story_type)

    # Output to file or Notion
    if approval_pack:
        filepath = None
        notion_url = None

        if notion_enabled:
            try:
                from notion_integration import create_notion_page
                notion_url = create_notion_page(approval_pack)
                print(f"\n[+] Post pushed to Notion: {notion_url}")
            except Exception as e:
                print(f"\n[!] Notion integration failed: {e}")
                print("[*] Falling back to file save...")
                from draft_generator import save_approval_pack
                filepath = save_approval_pack(approval_pack)
                print(f"\n[+] Post saved to: {filepath}")
        else:
            # Always save to file if Notion is not enabled
            from draft_generator import save_approval_pack
            filepath = save_approval_pack(approval_pack)
            print(f"\n[+] Post saved to: {filepath}")

        # Print to console
        print("\n" + "=" * 60)
        print("LINKEDIN POST")
        print("=" * 60)
        print()
        print(approval_pack)

        # Summary
        print("\n" + "=" * 60)
        print("Post ready!")
        print("=" * 60)

        if notion_url:
            print(f"\nReview in Notion: {notion_url}")
        if filepath:
            print(f"\nPost saved to: {filepath}")

        print("\nNext steps:")
        print("1. Review the post above")
        print("2. Edit to add more specific details if desired")
        print("3. Make it authentic to your voice")
        print("4. Post to LinkedIn when ready")


def print_header():
    """Print the tool header."""
    print("\n" + "=" * 60)
    print("LINKEDIN AI CONTENT CURATOR")
    print("=" * 60)
    print("\nThis tool helps you prepare LinkedIn posts about AI.")
    print("\nQUICK START:")
    print("  1. Auto-discover articles OR paste URLs (we'll auto-fetch titles)")
    print("  2. We'll select top 5 articles (mix of technical + general) and generate detailed posts")
    print("  3. Review in Notion and approve your favorites")
    print("  4. Auto-posts to LinkedIn within 2 hours")
    print()


def collect_articles() -> list[tuple[str, str]]:
    """
    Interactively collect article URLs from the user.
    Title is auto-fetched from the URL (optional to provide manually).

    Returns:
        List of (title, url) tuples
    """
    articles = []

    print("\n[TIP] Just paste the URL - we'll auto-fetch the title!")
    print("      (Or provide both title and URL if you prefer)")
    print()

    while True:
        print(f"\n--- Article {len(articles) + 1} ---")

        # Get URL first (more important)
        url = input("Article URL (press Enter to finish): ").strip()

        # Empty URL means we're done
        if not url:
            if articles:
                print("\n[*] Finished collecting articles.")
                break
            else:
                print("[!] Please add at least one article.")
                continue

        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            print("[!] Warning: URL should start with http:// or https://")
            print("[!] Proceeding anyway, but it may fail...")

        # Get title (optional)
        title = input("Article title (optional, press Enter to auto-fetch): ").strip()

        # If no title provided, we'll use a placeholder and fetch it later
        if not title:
            title = None  # Will be fetched from article

        articles.append((title, url))

        print(f"[+] Article added")

        # Ask if user wants to add more
        print()
        add_more = input("Add another article? (y/n, default=n): ").strip().lower()
        if add_more not in ['y', 'yes']:
            break

    return articles


def main():
    """Main execution flow."""
    print_header()

    # Check which generation mode is available
    api_provider = get_api_provider()
    notion_enabled = is_notion_configured()

    if api_provider:
        print(f"[+] AI Generation: Enabled (using {api_provider})")
    else:
        print("[!] AI Generation: Not configured (using template-based generation)")
        print("    Set ANTHROPIC_API_KEY or OPENAI_API_KEY to enable AI-powered insights")

    if notion_enabled:
        print("[+] Notion Integration: Enabled")
    else:
        print("[!] Notion Integration: Not configured (saving to file instead)")
        print("    Set NOTION_API_KEY and NOTION_DATABASE_ID to enable")

    print()

    # Ask user for article source
    print("=" * 60)
    print("ARTICLE SOURCE")
    print("=" * 60)
    print("\nHow would you like to get articles?")
    print("  1. Auto-discover (AI finds articles from news sources)")
    print("  2. Manual (paste your own URLs)")
    print()

    choice = input("Choose option (1 or 2, default=1): ").strip()

    # NEW: Ask for content type
    print("\n" + "=" * 60)
    print("CONTENT TYPE")
    print("=" * 60)
    print("\nWhat type of post would you like to create?")
    print("  1. Personal Experience (your own learnings)")
    print("  2. Learned from Colleagues/Team")
    print("  3. Technology Deep Dive (your perspective)")
    print("  4. Community Insights (meetups, conferences)")
    print("  5. Article-Based (auto-discovery or manual URLs)")
    print()

    content_type_choice = input("Choose content type (1-5, default=5): ").strip()

    # Map choice to content type
    if content_type_choice == '1':
        content_type = "personal_experience"
    elif content_type_choice == '2':
        content_type = "colleague_insight"
    elif content_type_choice == '3':
        content_type = "tech_perspective"
    elif content_type_choice == '4':
        content_type = "community_insight"
    else:
        content_type = "article_based"  # Default

    print(f"\n[*] Selected content type: {content_type}")

    # Handle non-article based content types (no articles needed)
    if content_type != "article_based":
        handle_non_article_content(content_type, api_provider, notion_enabled)
        return  # Exit after handling non-article content

    # Get articles (for article-based modes)
    articles = []

    if choice == '2':
        # Manual URL input
        article_inputs = collect_articles()

        if not article_inputs:
            print("\nNo articles provided. Exiting.")
            sys.exit(0)

        print(f"\n{'=' * 60}")
        print(f"Fetching {len(article_inputs)} article(s)...")
        print(f"{'=' * 60}")

        articles = fetch_multiple_articles(article_inputs)

    else:
        # Automatic discovery (default)
        print("\n[*] Auto-discovering articles from AI news sources...")
        print("    This may take a minute...")
        print("    Getting 20+ articles for AI to select top 5...")

        try:
            articles = discover_and_fetch(max_articles=20)  # Get more to choose top 5
        except Exception as e:
            print(f"\n[!] Auto-discovery failed: {e}")
            print("\nFalling back to manual URL input...")
            article_inputs = collect_articles()

            if not article_inputs:
                print("\nNo articles provided. Exiting.")
                sys.exit(0)

            articles = fetch_multiple_articles(article_inputs)

    if not articles:
        print("\n[!] No articles could be fetched. Please check the URLs and try again.")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"Successfully fetched {len(articles)} article(s)")
    print(f"{'=' * 60}")

    # Generate approval pack (AI or template-based)
    if api_provider:
        try:
            # Use AI to select and generate (pass mode for personal_experience vs traditional)
            approval_pack, provider_used = generate_approval_pack_ai(articles, mode=mode)
            print(f"\n[+] Generated with {provider_used} API")
        except Exception as e:
            print(f"\n[!] AI generation failed: {e}")
            print("[*] Falling back to template-based generation...")
            best_articles = select_best_articles(articles, max_options=5)
            approval_pack = generate_approval_pack(best_articles)
    else:
        # Use template-based generation
        print("\nAnalyzing and ranking articles...")
        best_articles = select_best_articles(articles, max_options=10)
        print(f"\nSelected {len(best_articles)} best article(s) for review.")
        print("\nGenerating approval pack...")
        approval_pack = generate_approval_pack(best_articles)

    # Output to file or Notion
    filepath = None
    notion_url = None

    if notion_enabled:
        try:
            # Check if there are multiple articles (look for "ARTICLE 1:" etc)
            if "ARTICLE 1:" in approval_pack or "ARTICLE 2:" in approval_pack:
                print("\n[*] Creating separate Notion pages for each article...")
                notion_urls = create_notion_pages_for_articles(approval_pack)
                print(f"\n[+] Created {len(notion_urls)} Notion pages")
                print("\nYou can now:")
                print("  • Review each article separately")
                print("  • Approve only the ones you want to post")
                print("  • Delete pages for articles you don't want")
                print(f"\nNotion pages:")
                for i, url in enumerate(notion_urls, 1):
                    print(f"  {i}. {url}")
            else:
                # Single article - create one page
                notion_url = create_notion_page(approval_pack)
                print(f"\n[+] Approval pack pushed to Notion: {notion_url}")
        except Exception as e:
            print(f"\n[!] Notion integration failed: {e}")
            print("[*] Falling back to file save...")
            filepath = save_approval_pack(approval_pack)
            print(f"\n[+] Approval pack saved to: {filepath}")
    else:
        # Always save to file if Notion is not enabled
        filepath = save_approval_pack(approval_pack)
        print(f"\n[+] Approval pack saved to: {filepath}")

    # Print to console
    print("\n" + "=" * 60)
    print("APPROVAL PACK")
    print("=" * 60)
    print()
    print(approval_pack)

    # Summary
    print("\n" + "=" * 60)
    print("Review complete!")
    print("=" * 60)

    if notion_url:
        print(f"\nReview and approve in Notion: {notion_url}")
    if filepath:
        print(f"\nDraft saved to: {filepath}")

    print("\nNext steps:")
    print("1. Review the approval pack above")
    print("2. Edit the LinkedIn draft if needed")
    print("3. Copy and post to LinkedIn manually")
    if notion_url:
        print("4. Update status to 'Posted' in Notion after publishing")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] An error occurred: {e}")
        sys.exit(1)

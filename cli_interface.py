#!/usr/bin/env python3
"""
CLI Interface - Command-line interface for LinkedIn content generation.

Supports all content types via command-line arguments for quick,
scriptable post generation.
"""

import sys
import argparse
from typing import Optional


def parse_cli_args() -> dict:
    """
    Parse command-line arguments for LinkedIn content generation.

    Returns:
        Dictionary with parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate LinkedIn posts from command line',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Colleague insight
  python linkedin_curator.py --type colleague --name "Sarah Chen" --topic "LLM hallucinations" --learned "She showed me a fact-checking technique"

  # Tech perspective
  python linkedin_curator.py --type tech --technology "RAG systems" --experience "6 months in production" --perspective "what papers don't tell you"

  # Community insight
  python linkedin_curator.py --type community --event "AI meetup" --topic "prompt engineering" --heard "Write prompts like explaining to an intern"

  # Personal experience
  python linkedin_curator.py --type personal --topic "A mistake I made with AI deployment"

  # Article-based (auto-discovery)
  python linkedin_curator.py --type article --source auto

  # Article-based (manual URLs)
  python linkedin_curator.py --type article --source manual --urls "url1,url2"
        """
    )

    parser.add_argument(
        '--type',
        choices=['colleague', 'tech', 'community', 'personal', 'article'],
        help='Content type to generate'
    )

    # Colleague insight arguments
    parser.add_argument('--name', help='Colleague name (for colleague type)')
    parser.add_argument('--learned', help='What you learned (for colleague type)')

    # Tech perspective arguments
    parser.add_argument('--technology', help='Technology/tool/framework (for tech type)')
    parser.add_argument('--experience', help='Your experience level (for tech type)')
    parser.add_argument('--perspective', help='Perspective focus (for tech type)')
    parser.add_argument('--insights', help='Specific insights (optional, for tech type)')

    # Community insight arguments
    parser.add_argument('--event', help='Event type (for community type)')
    parser.add_argument('--heard', help='What you heard (for community type)')

    # Personal experience arguments
    parser.add_argument('--topic', help='Topic for personal experience or community type')
    parser.add_argument('--story-type', choices=['professional_learning', 'challenge_overcome', 'insight_gained', 'career_moment'],
                       help='Type of personal story (for personal type)')
    parser.add_argument('--length', choices=['short', 'medium', 'long'],
                       help='Post length (for personal type)')

    # Article-based arguments
    parser.add_argument('--source', choices=['auto', 'manual'], help='Article source (for article type)')
    parser.add_argument('--urls', help='Comma-separated article URLs (for manual source)')

    # Common arguments
    parser.add_argument('--output', choices=['notion', 'file', 'console'],
                       default='notion', help='Output destination (default: notion)')
    parser.add_argument('--save', help='Save output to file (specify path)')
    parser.add_argument('--provider', choices=['claude', 'openai', 'template'],
                       help='AI provider to use (default: auto-detect)')

    args = parser.parse_args()

    # Convert to dictionary
    return vars(args)


def validate_cli_args(args: dict) -> tuple[bool, Optional[str]]:
    """
    Validate CLI arguments.

    Args:
        args: Parsed arguments dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not args.get('type'):
        return False, "Content type (--type) is required"

    content_type = args['type']

    # Validate colleague type
    if content_type == 'colleague':
        if not args.get('name'):
            return False, "--name is required for colleague type"
        if not args.get('learned'):
            return False, "--learned is required for colleague type"
        if not args.get('topic'):
            return False, "--topic is required for colleague type"

    # Validate tech type
    elif content_type == 'tech':
        if not args.get('technology'):
            return False, "--technology is required for tech type"
        if not args.get('experience'):
            return False, "--experience is required for tech type"
        if not args.get('perspective'):
            return False, "--perspective is required for tech type"

    # Validate community type
    elif content_type == 'community':
        if not args.get('event'):
            return False, "--event is required for community type"
        if not args.get('topic'):
            return False, "--topic is required for community type"
        if not args.get('heard'):
            return False, "--heard is required for community type"

    # Validate personal type
    elif content_type == 'personal':
        if not args.get('topic'):
            return False, "--topic is required for personal type"

    # Validate article type
    elif content_type == 'article':
        if args.get('source') == 'manual' and not args.get('urls'):
            return False, "--urls is required when --source is manual"

    return True, None


def execute_cli_command(args: dict) -> str:
    """
    Execute the LinkedIn post generation based on CLI arguments.

    Args:
        args: Parsed and validated arguments

    Returns:
        Generated post content
    """
    from dotenv import load_dotenv
    load_dotenv()

    import os
    from notion_integration import is_notion_configured, create_notion_page
    from draft_generator import save_approval_pack

    # Determine AI provider
    provider = args.get('provider')
    if not provider:
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = "claude"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            provider = "template"

    content_type = args['type']
    result = None

    # Execute based on content type
    if content_type == 'colleague':
        from multi_mode_generator import (
            generate_colleague_insight_with_claude,
            generate_colleague_insight_with_openai,
            generate_template_colleague_insight
        )

        print(f"\n[*] Generating colleague insight post...")
        print(f"[*] Colleague: {args['name']}")
        print(f"[*] Topic: {args['topic']}")

        if provider == "claude":
            result = generate_colleague_insight_with_claude(
                args['name'],
                args['topic'],
                args['learned']
            )
        elif provider == "openai":
            result = generate_colleague_insight_with_openai(
                args['name'],
                args['topic'],
                args['learned']
            )
        else:
            result = generate_template_colleague_insight(
                args['name'],
                args['topic'],
                args['learned']
            )

    elif content_type == 'tech':
        from multi_mode_generator import (
            generate_tech_perspective_with_claude,
            generate_tech_perspective_with_openai,
            generate_template_tech_perspective
        )

        print(f"\n[*] Generating tech perspective post...")
        print(f"[*] Technology: {args['technology']}")
        print(f"[*] Experience: {args['experience']}")

        if provider == "claude":
            result = generate_tech_perspective_with_claude(
                args['technology'],
                args['experience'],
                args['perspective'],
                args.get('insights', '')
            )
        elif provider == "openai":
            result = generate_tech_perspective_with_openai(
                args['technology'],
                args['experience'],
                args['perspective'],
                args.get('insights', '')
            )
        else:
            result = generate_template_tech_perspective(
                args['technology'],
                args['experience'],
                args['perspective']
            )

    elif content_type == 'community':
        from multi_mode_generator import (
            generate_community_insight_with_claude,
            generate_community_insight_with_openai,
            generate_template_community_insight
        )

        print(f"\n[*] Generating community insight post...")
        print(f"[*] Event: {args['event']}")
        print(f"[*] Topic: {args['topic']}")

        if provider == "claude":
            result = generate_community_insight_with_claude(
                args['event'],
                args['topic'],
                args['heard']
            )
        elif provider == "openai":
            result = generate_community_insight_with_openai(
                args['event'],
                args['topic'],
                args['heard']
            )
        else:
            result = generate_template_community_insight(
                args['event'],
                args['topic'],
                args['heard']
            )

    elif content_type == 'personal':
        from personal_story_generator import (
            generate_personal_story_with_claude,
            generate_personal_story_with_openai,
            generate_template_personal_story
        )

        print(f"\n[*] Generating personal experience post...")
        print(f"[*] Topic: {args['topic']}")

        story_type = args.get('story_type', 'professional_learning')
        length = args.get('length', 'medium')

        if provider == "claude":
            result = generate_personal_story_with_claude(args['topic'], story_type, length)
        elif provider == "openai":
            result = generate_personal_story_with_openai(args['topic'], story_type, length)
        else:
            result = generate_template_personal_story(args['topic'], story_type)

    elif content_type == 'article':
        # Article-based generation (call main script)
        print("\n[*] Article-based generation")
        print("[*] This mode uses the full article discovery pipeline")
        print("[*] Please use the main interactive mode or see README")
        return "Article-based mode requires interactive mode. Use: python linkedin_curator.py"

    # Handle output
    output = args.get('output', 'notion')
    notion_enabled = is_notion_configured()

    if output == 'notion' and notion_enabled:
        try:
            notion_url = create_notion_page(result)
            print(f"\n[+] Post pushed to Notion: {notion_url}")
        except Exception as e:
            print(f"\n[!] Notion integration failed: {e}")
            print("[*] Falling back to file save...")
            filepath = save_approval_pack(result)
            print(f"\n[+] Post saved to: {filepath}")
    elif output == 'file' or args.get('save'):
        save_path = args.get('save')
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"\n[+] Post saved to: {save_path}")
        else:
            filepath = save_approval_pack(result)
            print(f"\n[+] Post saved to: {filepath}")

    # Always print to console
    print("\n" + "=" * 70)
    print("GENERATED POST")
    print("=" * 70)
    print()
    print(result)

    return result


def main_cli():
    """Main entry point for CLI mode."""
    args = parse_cli_args()

    # Validate arguments
    is_valid, error_msg = validate_cli_args(args)
    if not is_valid:
        print(f"[!] Error: {error_msg}")
        print("\nUse --help for usage information")
        sys.exit(1)

    # Execute command
    try:
        result = execute_cli_command(args)
        print("\n[+] Post generated successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error generating post: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main_cli()

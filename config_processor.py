#!/usr/bin/env python3
"""
Config Processor - Process YAML config files for batch content generation.

Allows planning multiple posts in advance and generating them in batch.
"""

import os
import sys
from typing import Optional
from datetime import datetime


def load_content_plan(config_path: str = "content_plan.yml") -> Optional[dict]:
    """
    Load content plan from YAML config file.

    Args:
        config_path: Path to YAML config file

    Returns:
        Dictionary with content plan or None if error
    """
    try:
        import yaml
    except ImportError:
        print("[!] PyYAML not installed. Run: pip install pyyaml")
        print("[*] Falling back to manual mode")
        return None

    if not os.path.exists(config_path):
        print(f"[!] Config file not found: {config_path}")
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        print(f"[+] Loaded config from: {config_path}")
        return config
    except Exception as e:
        print(f"[!] Error loading config: {e}")
        return None


def validate_config(config: dict) -> tuple[bool, Optional[str]]:
    """
    Validate content plan configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not config:
        return False, "Config is empty"

    if 'posts' not in config:
        return False, "Config must contain 'posts' key"

    posts = config['posts']

    if not isinstance(posts, list):
        return False, "'posts' must be a list"

    if len(posts) == 0:
        return False, "No posts defined in config"

    # Validate each post
    required_fields_by_type = {
        'personal': ['topic'],
        'colleague': ['name', 'topic', 'learned'],
        'tech': ['technology', 'experience', 'perspective'],
        'community': ['event', 'topic', 'heard'],
        'article': ['source']
    }

    for i, post in enumerate(posts):
        if not isinstance(post, dict):
            return False, f"Post {i+1} must be a dictionary"

        post_type = post.get('type')

        if not post_type:
            return False, f"Post {i+1} missing 'type' field"

        if post_type not in required_fields_by_type:
            return False, f"Post {i+1} has unknown type: {post_type}"

        required_fields = required_fields_by_type[post_type]
        for field in required_fields:
            if field not in post:
                return False, f"Post {i+1} (type: {post_type}) missing required field: {field}"

    return True, None


def process_content_plan(config: dict, api_provider: Optional[str] = None) -> list[str]:
    """
    Process content plan and generate all posts.

    Args:
        config: Validated configuration dictionary
        api_provider: AI provider to use (claude, openai, template)

    Returns:
        List of generated post contents
    """
    from dotenv import load_dotenv
    load_dotenv()

    import os
    from notion_integration import is_notion_configured
    try:
        from notion_integration_v2 import create_notion_page_improved as create_notion_page
        print("[*] Using improved Notion formatting")
    except ImportError:
        from notion_integration import create_notion_page
        print("[*] Using standard Notion formatting")
    from draft_generator import save_approval_pack

    # Determine AI provider if not specified
    if not api_provider:
        if os.getenv("ANTHROPIC_API_KEY"):
            api_provider = "claude"
        elif os.getenv("OPENAI_API_KEY"):
            api_provider = "openai"
        else:
            api_provider = "template"

    posts = config['posts']
    notion_enabled = is_notion_configured()
    results = []

    print(f"\n[*] Processing {len(posts)} post(s)...")
    print(f"[*] AI Provider: {api_provider}")
    print()

    for i, post_config in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] Processing post {i}...")
        print(f"    Type: {post_config['type']}")

        try:
            result = process_single_post(post_config, api_provider)
            results.append(result)

            # Save to Notion or file
            if notion_enabled:
                try:
                    notion_url = create_notion_page(result)
                    print(f"    [+] Saved to Notion: {notion_url}")
                except Exception as e:
                    print(f"    [!] Notion failed: {e}")
                    filepath = save_approval_pack(result)
                    print(f"    [+] Saved to file: {filepath}")
            else:
                filepath = save_approval_pack(result)
                print(f"    [+] Saved to file: {filepath}")

            print(f"    [+] Post {i} generated successfully")
            print()

        except Exception as e:
            print(f"    [!] Failed to generate post {i}: {e}")
            print()

    print(f"\n[*] Generated {len(results)}/{len(posts)} post(s) successfully")

    return results


def process_single_post(post_config: dict, api_provider: str) -> str:
    """
    Process a single post from config.

    Args:
        post_config: Single post configuration
        api_provider: AI provider to use

    Returns:
        Generated post content
    """
    post_type = post_config['type']

    if post_type == 'colleague':
        from multi_mode_generator import (
            generate_colleague_insight_with_claude,
            generate_colleague_insight_with_openai,
            generate_template_colleague_insight
        )

        if api_provider == "claude":
            return generate_colleague_insight_with_claude(
                post_config['name'],
                post_config['topic'],
                post_config['learned'],
                post_config.get('experience', '')
            )
        elif api_provider == "openai":
            return generate_colleague_insight_with_openai(
                post_config['name'],
                post_config['topic'],
                post_config['learned'],
                post_config.get('experience', '')
            )
        else:
            return generate_template_colleague_insight(
                post_config['name'],
                post_config['topic'],
                post_config['learned']
            )

    elif post_type == 'tech':
        from multi_mode_generator import (
            generate_tech_perspective_with_claude,
            generate_tech_perspective_with_openai,
            generate_template_tech_perspective
        )

        if api_provider == "claude":
            return generate_tech_perspective_with_claude(
                post_config['technology'],
                post_config['experience'],
                post_config['perspective'],
                post_config.get('insights', '')
            )
        elif api_provider == "openai":
            return generate_tech_perspective_with_openai(
                post_config['technology'],
                post_config['experience'],
                post_config['perspective'],
                post_config.get('insights', '')
            )
        else:
            return generate_template_tech_perspective(
                post_config['technology'],
                post_config['experience'],
                post_config['perspective']
            )

    elif post_type == 'community':
        from multi_mode_generator import (
            generate_community_insight_with_claude,
            generate_community_insight_with_openai,
            generate_template_community_insight
        )

        if api_provider == "claude":
            return generate_community_insight_with_claude(
                post_config['event'],
                post_config['topic'],
                post_config['heard'],
                post_config.get('context', '')
            )
        elif api_provider == "openai":
            return generate_community_insight_with_openai(
                post_config['event'],
                post_config['topic'],
                post_config['heard'],
                post_config.get('context', '')
            )
        else:
            return generate_template_community_insight(
                post_config['event'],
                post_config['topic'],
                post_config['heard']
            )

    elif post_type == 'personal':
        from personal_story_generator import (
            generate_personal_story_with_claude,
            generate_personal_story_with_openai,
            generate_template_personal_story
        )

        story_type = post_config.get('story_type', 'professional_learning')
        length = post_config.get('length', 'medium')

        if api_provider == "claude":
            return generate_personal_story_with_claude(
                post_config['topic'],
                story_type,
                length
            )
        elif api_provider == "openai":
            return generate_personal_story_with_openai(
                post_config['topic'],
                story_type,
                length
            )
        else:
            return generate_template_personal_story(
                post_config['topic'],
                story_type
            )

    else:
        raise ValueError(f"Unknown post type: {post_type}")


def create_example_config(output_path: str = "content_plan.yml"):
    """
    Create an example content plan config file.

    Args:
        output_path: Where to save the example config
    """
    example_config = """# LinkedIn Content Plan
# Generate multiple posts at once using this config file

week_of: "2025-02-18"

posts:
  # Personal Experience
  - type: personal
    topic: A mistake I made with AI deployment
    story_type: challenge_overcome
    length: medium

  # Learned from Colleague
  - type: colleague
    name: Sarah Chen
    topic: LLM hallucination techniques
    learned: She showed me a fact-checking prompt technique that uses opposing viewpoints
    experience: I've been fighting hallucinations for months

  # Technology Perspective
  - type: tech
    technology: RAG systems
    experience: 6 months in production
    perspective: what papers don't tell you
    insights: Chunk size matters more than anyone admits, hybrid search wins

  # Community Insight
  - type: community
    event: AI meetup
    topic: Prompt engineering tips
    heard: Someone suggested writing prompts like you're explaining to a smart intern
    context: I tried this the next day and it worked great

  # More examples...
  # - type: colleague
  #   name: Mike Johnson
  #   topic: Database optimization
  #   learned: Composite indexes changed everything for our query performance
  #
  # - type: tech
  #   technology: LangChain
  #   experience: 1 year of use
  #   perspective: production reality vs hype
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(example_config)

    print(f"[+] Created example config: {output_path}")
    print("[*] Edit this file with your content and run:")
    print("    python linkedin_curator.py --config content_plan.yml")


if __name__ == "__main__":
    import sys

    # Check if user wants to create example config
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        create_example_config()
        sys.exit(0)

    # Otherwise, process config file
    config_path = sys.argv[1] if len(sys.argv) > 1 else "content_plan.yml"

    print("=" * 70)
    print("CONTENT PLAN PROCESSOR")
    print("=" * 70)
    print()

    # Load config
    config = load_content_plan(config_path)
    if not config:
        sys.exit(1)

    # Validate config
    is_valid, error_msg = validate_config(config)
    if not is_valid:
        print(f"[!] Validation error: {error_msg}")
        sys.exit(1)

    print("[+] Config validated successfully")
    print()

    # Process posts
    results = process_content_plan(config)

    # Summary
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\nGenerated {len(results)} post(s)")
    print("\nNext steps:")
    print("1. Review generated posts in Notion or files")
    print("2. Edit to add personal details and authenticity")
    print("3. Approve and post to LinkedIn")

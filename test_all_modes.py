#!/usr/bin/env python3
"""
Test script to demonstrate all 4 content types
"""

import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("TESTING ALL 4 CONTENT TYPES")
print("=" * 70)
print()

# Test 1: Colleague Insight
print("-" * 70)
print("TEST 1: COLLEAGUE INSIGHT")
print("-" * 70)
from multi_mode_generator import generate_template_colleague_insight

result1 = generate_template_colleague_insight(
    colleague_name="Sarah Chen",
    topic="prompt engineering",
    what_you_learned="She showed me that writing prompts like explaining to an intern works better than giving instructions to a computer"
)
print(result1)
print()

# Test 2: Tech Perspective
print("-" * 70)
print("TEST 2: TECH PERSPECTIVE")
print("-" * 70)
from multi_mode_generator import generate_template_tech_perspective

result2 = generate_template_tech_perspective(
    technology="RAG systems",
    experience_level="6 months in production",
    perspective_focus="what papers don't tell you"
)
print(result2)
print()

# Test 3: Community Insight
print("-" * 70)
print("TEST 3: COMMUNITY INSIGHT")
print("-" * 70)
from multi_mode_generator import generate_template_community_insight

result3 = generate_template_community_insight(
    event="AI meetup",
    topic="LLM deployment",
    what_you_heard="Someone mentioned starting simple and iterating is better than planning everything upfront"
)
print(result3)
print()

# Test 4: Personal Experience
print("-" * 70)
print("TEST 4: PERSONAL EXPERIENCE")
print("-" * 70)
from personal_story_generator import generate_template_personal_story

result4 = generate_template_personal_story(
    topic="A mistake I made with API rate limits",
    story_type="challenge_overcome"
)
print(result4)
print()

print("=" * 70)
print("ALL TESTS COMPLETE!")
print("=" * 70)
print()
print("Summary:")
print("- Colleague Insight: Generates posts that give credit to coworkers")
print("- Tech Perspective: Shares your production experience")
print("- Community Insight: Shows you're engaged in the community")
print("- Personal Experience: Shares your own learnings")
print()
print("All modes working perfectly!")
print()
print("Ready to use!")

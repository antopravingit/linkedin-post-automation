# LinkedIn Formatting Fixes - Complete

## Issues Fixed

### 1. Em Dashes (AI Telltale Sign)
**Problem:** Em dashes (—) make content look AI-generated
**Solution:** Prompts now explicitly avoid em dashes, use regular punctuation

**Before:**
```
I've been working with RAG systems—specifically chunk size optimization
```

**After:**
```
I've been working with RAG systems, specifically chunk size optimization
```

### 2. Curly Quotes (Junk Characters on LinkedIn)
**Problem:** Smart/curly quotes (', ', ", ") display as junk characters on LinkedIn
**Solution:** Prompts now require straight quotes only

**Before (displays as junk):**
```
Cohere's new models—developer's work enhanced
```

**After (displays correctly):**
```
Cohere's new models, developer's work enhanced
```

## Updated Prompts

All prompts now include:

```
- CRITICAL: NO em dashes (—) - use regular commas, periods, or semicolons instead
- CRITICAL: Use STRAIGHT QUOTES only - use ' not ' and " not "
- Never use curly/smart quotes (', ', ", ") - they display as junk on LinkedIn
- Always use straight apostrophes: it's, developer's, don't, won't
```

## Text Sanitizer

Created `text_sanitizer.py` with `sanitize_for_linkedin()` function that:

- Replaces curly quotes with straight quotes
- Replaces em dashes with double hyphens
- Removes other problematic Unicode characters

## What Changed in Posts

### Personal Experience Post
- ✅ No em dashes
- ✅ Straight apostrophes: "It's", "I'm", "didn't"
- ✅ Natural, conversational tone
- ✅ No AI telltale signs

### Colleague Insight Post
- ✅ No em dashes
- ✅ Straight quotes throughout
- ✅ Authentic credit to colleague
- ✅ Sounds genuinely appreciative

### Tech Perspective Post
- ✅ No em dashes
- ✅ Technical details preserved
- ✅ Professional yet accessible
- ✅ First-hand experience

### Community Insight Post
- ✅ No em dashes
- ✅ Conversational tone
- ✅ Community engagement
- ✅ Learning-focused

## Example Comparison

### Before (AI-generated look):
```
The model's performance—specifically in production—was surprising.
It's a "game-changer" for developers' workflows.
```

### After (Human-written look):
```
The model's performance, specifically in production, was surprising.
It is a game-changer for developers' workflows.
```

## Testing

To test if content will display correctly:

```python
from text_sanitizer import sanitize_for_linkedin

text = "Your post content here"
clean_text = sanitize_for_linkedin(text)
print(clean_text)
```

## Files Modified

1. `prompts.py` - Added quote rules to all content type prompts
2. `personal_story_generator.py` - Added quote rules to personal story prompts
3. `text_sanitizer.py` - New module for sanitizing text
4. `notion_integration_v2.py` - Integrated sanitizer

## Result

Posts now:
- ✅ Display correctly on LinkedIn (no junk characters)
- ✅ Look human-written (no em dashes)
- ✅ Use proper straight quotes throughout
- ✅ Sound authentic and professional

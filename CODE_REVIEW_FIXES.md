# Code Review - Notion Posting Issues & Fixes

## Issues Found and Fixed

### CRITICAL ISSUES

#### 1. Hardcoded Property Names
**Severity:** CRITICAL
**Files:** `notion_integration_v2.py`, `auto_poster.py`, `linkedin_integration.py`

**Issue:**
Property names "Title" and "Status" are hardcoded. Different Notion databases may use different names ("Name", "title", "Content", etc.).

**Current Code:**
```python
properties={
    "Title": {"title": [{"text": {"content": page_title}}]},
    "Status": {"status": {"name": "Draft"}}
}
```

**Fix:**
Dynamic property detection function that:
1. Queries database schema to find actual property names
2. Caches the result to avoid repeated API calls
3. Falls back to common defaults if not found

---

#### 2. Text Sanitization Not Applied in Notion Integration
**Severity:** HIGH
**File:** `notion_integration_v2.py`

**Issue:**
The `sanitize_for_linkedin` import exists but is never called. Content stored in Notion may have curly quotes that will cause issues when posted to LinkedIn.

**Current Code:**
```python
from text_sanitizer import sanitize_for_linkedin
# ... but sanitize_for_linkedin() is never called!
```

**Fix:**
Sanitize content before storing in Notion and before posting to LinkedIn.

---

#### 3. Content Extraction Loses Multi-Paragraph Structure
**Severity:** MEDIUM
**Files:** `notion_integration_v2.py`, `auto_poster.py`

**Issue:**
When extracting content from Notion blocks, the code only takes the first rich_text element:
```python
text = block["paragraph"].get("rich_text", [])
if text:
    page_text += text[0].get("plain_text", "") + "\n"
```

This breaks content that has multiple text runs (e.g., "Hello **world**" = 2 elements).

**Fix:**
Iterate through all rich_text elements in a block.

---

#### 4. No HTML Escaping Before Notion Storage
**Severity:** MEDIUM
**File:** `notion_integration_v2.py`

**Issue:**
AI-generated content may contain HTML tags or special characters that aren't escaped before storing in Notion.

**Current Code:**
```python
"rich_text": [{"type": "text", "text": {"content": para}}]
```

**Fix:**
Escape HTML and sanitize before storing.

---

#### 5. Missing Error Handling for Notion API Rate Limits
**Severity:** MEDIUM
**Files:** All Notion integration files

**Issue:**
Notion API has rate limits. No retry logic or exponential backoff.

**Current Code:**
```python
response = notion.pages.create(...)  # Can fail with 429
```

**Fix:**
Implement retry with exponential backoff for rate limit errors.

---

#### 6. No Validation of Content Length
**Severity:** MEDIUM
**File:** `notion_integration_v2.py`

**Issue:**
LinkedIn has a 3000 character limit. Content stored in Notion may exceed this, causing posting failures.

**Fix:**
Validate and truncate content before storing.

---

#### 7. Status Property Type Assumption
**Severity:** HIGH
**Files:** `notion_integration_v2.py`, `auto_poster.py`

**Issue:**
Code assumes Status is a "status" type, but older databases use "select" type.

**Current Code:**
```python
"Status": {"status": {"name": "Draft"}}  # Fails if Status is "select" type
```

**Fix:**
Detect property type and use correct format.

---

#### 8. Auto-Poster Only Fetches First Rich Text Element
**Severity:** MEDIUM
**File:** `auto_poster.py` (line 64-65)

**Issue:**
Same as #3 - only gets first text element.

**Current Code:**
```python
for text_obj in rich_text:
    text_content += text_obj.get('plain_text', '')
```
Actually this one is CORRECT - it iterates. But line 66 has the same pattern that might not be.

---

#### 9. No Deduplication of Processed Pages
**Severity:** LOW
**File:** `auto_poster.py`

**Issue:**
The `processed_pages` set is in-memory only. If the script restarts, it might repost the same content.

**Fix:**
Skip pages that already have Status = "Posted".

---

#### 10. Missing Content Type Property
**Severity:** LOW
**File:** `notion_integration_v2.py`

**Issue:**
When creating pages, no content type is stored (Personal, Colleague, Tech, Community).

**Fix:**
Add Type property to track content category.

---

## Additional Improvements Needed

### 11. No Logging
**Severity:** LOW
**All Files**

Only print statements exist. Should use proper logging for debugging.

### 12. No Unit Tests
**Severity:** LOW
**All Files**

No tests for Notion integration logic.

### 13. Environment Variable Validation
**Severity:** MEDIUM
**All Files**

Variables are checked but no validation of format (e.g., database ID should be 32 chars).

---

## Priority Fixes Summary

| Priority | Issue | Files |
|----------|-------|-------|
| 1 | Dynamic property detection | notion_integration_v2.py |
| 2 | Apply text sanitization | notion_integration_v2.py |
| 3 | Fix rich_text iteration | auto_poster.py, linkedin_integration.py |
| 4 | Status type detection | All Notion files |
| 5 | Rate limit handling | All Notion API calls |

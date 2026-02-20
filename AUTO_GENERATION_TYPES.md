# What Type of Posts Are Automatically Generated?

## 📊 Current Automatic Workflow

### Default Behavior (Mon/Wed/Fri 9 AM)

The GitHub Actions workflow generates **Article-Based posts** with **"Personal Experience"** perspective.

**What this means:**
- ✅ Auto-discovers 5 AI articles from news sources
- ✅ Generates posts in **first-person** perspective ("I learned", "Reading this I discovered")
- ✅ Each post is about an interesting AI article
- ✅ Format: "I just read this article about X, here's what I learned..."

---

## 📝 Example Auto-Generated Post

```markdown
I just read some fascinating research about RAG systems that really
made me think.

The paper discusses how chunk size affects retrieval accuracy in ways
most documentation doesn't cover. After 6 months of working with RAG
in production, I can confirm this is absolutely critical.

What surprised me most: smaller chunks (around 150 words) consistently
outperformed larger ones, despite what the theory suggests.

This is why I love reading research - it always challenges my assumptions
and shows me what's actually working in practice.
```

---

## 🎯 5 Content Types Available

### 1. Personal Experience (Default for Auto-Generation)
**What:** Your own learnings, mistakes, insights
**Generated:** From articles with "I learned" framing
**Example:** "I just read about X, here's what I learned..."

### 2. Learned from Colleagues
**What:** Credit to coworkers/teammates
**Generated:** Manual input required
**Example:** "Sarah Chen showed me a technique for..."

### 3. Technology Deep Dive
**What:** Your technical perspective on tools
**Generated:** Manual input required
**Example:** "I've been using RAG for 6 months, here's my take..."

### 4. Community Insights
**What:** Learnings from meetups/conferences
**Generated:** Manual input required
**Example:** "At the AI meetup yesterday, someone mentioned..."

### 5. Article-Based (Current Auto-Generation)
**What:** AI article summaries in first-person
**Generated:** Fully automatic
**Example:** "I just read research about X, here's what struck me..."

---

## 🔄 How to Change Auto-Generation Type

### Option 1: Use Config File (Recommended)

Create `content_plan.yml` in your repo:
```yaml
week_of: "2025-02-18"

posts:
  # Mix of different types
  - type: colleague
    name: Sarah Chen
    topic: LLM hallucinations
    learned: Fact-checking prompts

  - type: tech
    technology: RAG systems
    experience: 6 months
    perspective: Production reality

  - type: community
    event: AI meetup
    topic: Prompt engineering
    heard: Write like explaining to interns
```

Then update GitHub Actions to use config:
```yaml
- name: Run LinkedIn Curator
  run: |
    python config_processor.py content_plan.yml
```

### Option 2: Mix Article + Personal Posts

Modify the workflow to alternate:
```yaml
# Monday: Articles
# Wednesday: Personal stories
# Friday: Community insights
```

### Option 3: Manual Selection (Current)

Run different generators manually:
```bash
# Generate colleague insight
python linkedin_curator.py
# Choose option 2 (Colleague)

# Generate tech perspective
python linkedin_curator.py
# Choose option 3 (Tech)

# Generate from config (all types)
python config_processor.py content_plan.yml
```

---

## 📊 Comparison

| Content Type | Auto-Generated? | Content Source | Engagement |
|--------------|-----------------|----------------|------------|
| **Article-Based** | ✅ Yes (default) | AI articles | Medium |
| **Personal Experience** | ❌ Manual | Your stories | **High** |
| **Colleague Insight** | ❌ Manual | Team/coworkers | **High** |
| **Tech Perspective** | ❌ Manual | Your experience | **High** |
| **Community Insight** | ❌ Manual | Events/meetups | Medium |

---

## 💡 Recommendation

**For Maximum Engagement:**

1. **Keep Article-Based** for 1-2 posts per week (automatic, easy)
2. **Add Personal Posts** manually when you have experiences
3. **Add Colleague Posts** when you learn from coworkers
4. **Use Config File** to batch plan weekly content

**Example Week:**
- Monday: Auto-generate 5 article posts → Approve 2
- Tuesday: Manual colleague post about what Sarah taught you
- Wednesday: Auto-generate 5 article posts → Approve 1
- Thursday: Manual tech post about your RAG experience
- Friday: Auto-generate 5 article posts → Approve 2

**Result:** 5 high-quality posts, mixed types, 3-5x higher engagement!

---

## 🎛️ Quick Setup for Mixed Content

### Step 1: Create content_plan.yml
```yaml
week_of: "2025-02-18"

posts:
  - type: colleague
    name: Sarah Chen
    topic: AI ethics
    learned: She taught me about bias in datasets

  - type: tech
    technology: LangChain
    experience: 1 year
    perspective: What works in production
```

### Step 2: Generate when ready
```bash
python config_processor.py content_plan.yml
```

### Step 3: Let GitHub continue auto-generating articles
- They'll supplement your manual posts
- You'll have variety + consistency
- Best of both worlds!

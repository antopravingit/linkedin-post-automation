# Post Generation Modes - Which One to Use?

## Available Modes in GitHub Actions

### 1. **personal_experience** (Recommended - Default)
**What it does:**
- Generates article-based posts in **first-person** perspective
- Transforms "This article discusses X" → "I learned that X"
- Sounds like a real person sharing insights

**Example Output:**
> I just read some fascinating research about RAG systems that really made me think. The paper discusses how chunk size affects retrieval accuracy in ways most documentation doesn't cover. What struck me most: smaller chunks consistently outperformed larger ones. This is why I love reading research - it always challenges my assumptions.

**Best for:**
- ✅ Higher engagement (3-5x)
- ✅ Authentic voice
- ✅ Personal brand building
- ✅ Recommended for most use

---

### 2. **pure_personal**
**What it does:**
- Uses the personal story generator
- Generates posts about YOUR experiences (not from articles)
- Requires manual topic input (won't work in automated workflow)

**Example Output:**
> I remember the sinking feeling when our AI model crashed during deployment. We had overlooked data diversity in our training set. This taught me that context is everything in AI deployment.

**Best for:**
- ⚠️ NOT suitable for automated workflow
- ✅ Manual generation only (when you run it locally)
- ✅ For sharing personal stories

**Issue with GitHub Actions:**
- Requires interactive input
- Will FAIL in automated workflow
- Use locally instead: `python linkedin_curator.py --type personal`

---

### 3. **traditional**
**What it does:**
- Third-person perspective ("This article discusses...")
- Objective article summaries
- Lower engagement

**Example Output:**
> New research worth your time: This paper discusses RAG systems and how chunk size affects retrieval accuracy. The research shows smaller chunks perform better. Read more at [URL].

**Best for:**
- ⚠️ Lower engagement
- ⚠️ Sounds like a news bot
- ⚠️ Not recommended

---

## 🎯 Recommendation

### For Scheduled Automation (Mon/Wed/Fri)
**Use:** `personal_experience` (default)

This gives you:
- ✅ Authentic first-person voice
- ✅ Higher engagement
- ✅ No manual work required
- ✅ Works in automated workflow

### For Manual Generation (When You Want)
**Don't use GitHub Actions** - run locally instead:

```bash
# Personal stories
python linkedin_curator.py --type personal --topic "My mistake"

# Colleague insights
python linkedin_curator.py --type colleague --name "Sarah" --topic "AI"

# Tech perspectives
python linkedin_curator.py --type tech --technology "RAG" --experience "6 months"

# Community insights
python linkedin_curator.py --type community --event "Meetup" --topic "Prompts"

# Batch from config
python config_processor.py content_plan.yml
```

---

## 🔧 How to Manually Trigger GitHub Actions

### Option 1: Use Default Mode (Recommended)
1. Go to: https://github.com/antopravingit/linkedin-post-automation/actions
2. Click "Generate LinkedIn Content" workflow
3. Click "Run workflow" button
4. Leave mode as "personal_experience" (default)
5. Click "Run workflow"

### Option 2: Change Mode (If You Want)
1. Go to: https://github.com/antopravingit/linkedin-post-automation/actions
2. Click "Generate LinkedIn Content"
3. Click "Run workflow"
4. Select different mode if needed:
   - `personal_experience` - **Recommended** (first-person)
   - `traditional` - Third-person summaries (lower engagement)
   - `pure_personal` - **Won't work** (needs interactive input)
5. Click "Run workflow"

---

## ⚠️ Important Notes

### `pure_personal` Mode Will Fail
This mode requires interactive input and will **NOT work** in GitHub Actions. It will timeout with the same error you saw.

**Solution:** Use it locally instead:
```bash
python linkedin_curator.py
# Choose option 1 (Personal Experience)
```

### Recommended Setup
**Leave the scheduled workflow as `personal_experience`** (default)

This gives you:
- Automatic posts 3x/week
- First-person perspective ("I learned")
- Higher engagement
- No manual work needed

Then supplement with manual posts when inspiration strikes using the local commands above.

---

## 📊 Mode Comparison

| Mode | Perspective | Engagement | Automation | Recommended |
|------|-------------|------------|-------------|-------------|
| **personal_experience** | First-person ("I learned") | **High (3-5x)** | ✅ Works | ✅ **YES** |
| **traditional** | Third-person ("This article") | Low | ✅ Works | ❌ No |
| **pure_personal** | First-person (your stories) | **Highest** | ❌ Fails | ⚠️ Local only |

---

## ✅ Best Practice

**Scheduled Automation (GitHub Actions):**
- Mode: `personal_experience`
- Runs: Mon/Wed/Fri 9 AM CST
- Generates: 5 article-based posts
- You review and approve when convenient

**Manual Generation (Local):**
- Use CLI commands for other content types
- Capture ideas as they happen
- 30 seconds per post

**Result:** Best of both worlds - consistency + authenticity!

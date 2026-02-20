# Manual Post Generation - Quick Reference

## 1. PERSONAL EXPERIENCE (Fastest: 30 seconds)

**When:** You made a mistake, learned something, had an insight

**Command Line:**
```bash
python linkedin_curator.py --type personal --topic "My mistake with AI deployment"
```

**Interactive:**
```bash
python linkedin_curator.py
# Choose: 1 (Personal Experience)
# Enter your topic when prompted
```

**Example Topics:**
- "A mistake I made with API rate limits"
- "What I wish I knew earlier about debugging"
- "Insight from a recent project"

---

## 2. COLLEAGUE INSIGHT (Fastest: 30 seconds)

**When:** Someone taught you something, give credit

**Command Line:**
```bash
python linkedin_curator.py \
  --type colleague \
  --name "Sarah Chen" \
  --topic "LLM hallucinations" \
  --learned "She showed me a fact-checking prompt technique"
```

**Interactive:**
```bash
python linkedin_curator.py
# Choose: 2 (Learned from Colleagues)
# Enter name, topic, what you learned
```

**Example Topics:**
- "Sarah showed me prompt technique"
- "Mike taught me about database indexing"
- "Lead discussed ML deployment strategies"

---

## 3. TECH PERSPECTIVE (Fastest: 30 seconds)

**When:** You have hands-on experience with a technology

**Command Line:**
```bash
python linkedin_curator.py \
  --type tech \
  --technology "RAG systems" \
  --experience "6 months in production" \
  --perspective "what papers don't tell you"
```

**Interactive:**
```bash
python linkedin_curator.py
# Choose: 3 (Technology Deep Dive)
# Enter technology, experience, perspective
```

**Example Topics:**
- "RAG: 6 months production experience"
- "LangChain: what works, what doesn't"
- "Docker: lessons from 100+ containers"

---

## 4. COMMUNITY INSIGHT (Fastest: 30 seconds)

**When:** You attended a meetup, conference, workshop

**Command Line:**
```bash
python linkedin_curator.py \
  --type community \
  --event "AI meetup" \
  --topic "prompt engineering" \
  --heard "Write prompts like explaining to interns"
```

**Interactive:**
```bash
python linkedin_curator.py
# Choose: 4 (Community Insights)
# Enter event, topic, what you heard
```

**Example Topics:**
- "Meetup: prompt engineering tips"
- "Conference: new ML approach"
- "Discussion: debugging techniques"

---

## 5. BATCH GENERATION (Most Efficient: 5 minutes for 5+ posts)

**When:** You want to plan the whole week at once

**Step 1:** Create `content_plan.yml`
```yaml
week_of: "2025-02-18"

posts:
  - type: colleague
    name: Sarah Chen
    topic: LLM hallucinations
    learned: Fact-checking with opposing viewpoints

  - type: tech
    technology: RAG systems
    experience: 6 months
    perspective: Production reality vs theory

  - type: community
    event: AI meetup
    topic: Prompt engineering
    heard: Write like explaining to smart people

  - type: personal
    topic: Mistake I made with API rate limits
    story_type: challenge_overcome
```

**Step 2:** Generate all at once
```bash
python config_processor.py content_plan.yml
```

---

## Quick Cheat Sheet

| Type | Command | Time |
|------|---------|------|
| Personal | `--type personal --topic "topic"` | 30 sec |
| Colleague | `--type colleague --name "Name" --topic "Topic" --learned "Learned"` | 30 sec |
| Tech | `--type tech --technology "Tool" --experience "Time" --perspective "Take"` | 30 sec |
| Community | `--type community --event "Event" --topic "Topic" --heard "Heard"` | 30 sec |
| Batch | `config_processor.py content_plan.yml` | 5 min |

---

## Recommended Weekly Workflow

### Sunday (10 minutes)
1. Plan content for the week in `content_plan.yml`
2. Run: `python config_processor.py content_plan.yml`
3. All posts created in Notion

### Monday-Friday (2 minutes/day)
- Auto-generation also runs Mon/Wed/Fri
- Review posts in Notion when convenient
- Approve the ones you like
- Auto-poster publishes within 30 minutes

### Result
- 5-10 posts per week
- 15-20 minutes total time
- 3-5x higher engagement

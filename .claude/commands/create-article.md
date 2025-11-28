---
description: Generate full article from knowledge base via Cornelius
---

# Create Article Command

Call Cornelius in headless mode to generate a complete, long-form article from Eugene's knowledge base. Synthesizes multiple insights into coherent narrative with Eugene's authentic voice.

## Usage

```
/create-article <topic> <platform> [tone]
```

## Parameters

- **topic**: Article subject or theme
  - Specific: "AI agent adoption psychological barriers"
  - Broad: "The dopamine economy and social media"
  - Comparative: "Buddhism vs Neuroscience on consciousness"

- **platform**: Target platform (affects length and style)
  - `linkedin` - 800-1200 words, professional tone
  - `medium` - 1500-2500 words, depth-focused
  - `substack` - 1000-2000 words, newsletter style
  - `blog` - 1200-2000 words, comprehensive

- **tone** (optional): Override default tone
  - `professional` - Formal, authoritative
  - `casual` - Conversational, accessible (default for LinkedIn)
  - `contrarian` - Challenge conventional wisdom
  - `educational` - Teach concepts systematically

## Examples

### LinkedIn Article
```
/create-article "Why smart companies resist AI adoption" linkedin
```

### Medium Deep Dive
```
/create-article "The neuroscience of belief: Why changing minds is neurologically painful" medium
```

### Contrarian Take
```
/create-article "AI agents as digital organisms: A new framework" linkedin contrarian
```

### Educational Series
```
/create-article "Understanding dopamine: The motivation molecule" substack educational
```

## Workflow

1. **Format Prompt for Cornelius**
   - Specify article structure (intro, body, conclusion)
   - Request tone of voice profile application
   - Ask for permanent note citations throughout
   - Set word count target

2. **Call Cornelius (Headless Mode)**
   ```bash
   cd /Users/eugene/Dropbox/Agents/Cornelius
   claude -p "Create a [platform] article about [topic].

   Structure:
   - Compelling hook/introduction
   - 3-5 main sections with insights from permanent notes
   - Concrete examples and evidence
   - Actionable conclusion or provocative question

   Apply Eugene's [platform] tone of voice from the profile.
   Cite specific permanent notes in [brackets].
   Target: [word count] words.

   Focus on Eugene's unique/contrarian perspectives." \
   --output-format json --timeout 120000
   ```

3. **Parse Response**
   - Extract article text
   - Track cost (~$0.50-0.80 for article generation)
   - Note session_id

4. **Save Article**
   - Save to ContentHub/Prepared/articles/
   - Filename: `[topic-slug]-[date].md`
   - Include metadata: platform, tone, cost, cited notes

5. **Present to User**
   - Show article preview (first 200 words)
   - Display word count, estimated read time
   - Show cost and session info
   - Offer options: edit, post, schedule

## Article Structure

### LinkedIn (800-1200 words)
```
Hook (2-3 sentences)
↓
Context/Problem (1 paragraph)
↓
Insight 1 (2-3 paragraphs)
↓
Insight 2 (2-3 paragraphs)
↓
Insight 3 (2-3 paragraphs)
↓
Synthesis (1-2 paragraphs)
↓
CTA/Question (1-2 sentences)
```

### Medium (1500-2500 words)
```
Compelling narrative hook
↓
Background/Stakes
↓
Main Argument (3-5 sections)
  - Each section: Claim → Evidence → Example
  - Heavy permanent note citations
  - Contrarian or non-obvious angles
↓
Counterarguments addressed
↓
Synthesis and implications
↓
Conclusion with actionable takeaway
```

### Substack Newsletter (1000-2000 words)
```
Personal intro/anecdote
↓
"Here's what I've been thinking about..."
↓
2-3 main insights
  - Conversational tone
  - Direct address ("you")
  - Concrete examples
↓
What this means for you
↓
Call to action (reply, share, discuss)
```

## Response Format

```
📝 Article Generated: [Title]

Platform: LinkedIn
Word count: 1,047 words
Read time: ~5 minutes
Tone: Professional

Preview:
[First 200 words of article...]

📁 Saved to: ContentHub/Prepared/articles/ai-adoption-barriers-2025-11-14.md

📚 Cited Notes:
- [[AI adoption bottleneck is psychological not technical]]
- [[Professional identity creates AI resistance]]
- [[Finding a confirmation of the belief creates a spike of Dopamine]]
- [[Belief is a way to deal with Uncertainty]]

💰 Cost: $0.67
⏱️ Generation time: 18.3 seconds
🆔 Session: 54da041a-a181-4e35-a4f3-5cfe8bfe7596

---
Options:
1. Edit article
2. Post to LinkedIn now
3. Schedule for later
4. Save for manual review
```

## Prompt Engineering for Articles

### Comprehensive Prompt Template
```
Create a [PLATFORM] article about [TOPIC].

Structure:
- Hook: Start with [compelling question / surprising statistic / personal anecdote]
- Main body: 3-5 sections, each building on previous
- Synthesis: Connect insights to bigger picture
- Conclusion: [Actionable takeaway / Provocative question / Call to reflection]

Tone: [professional / casual / contrarian / educational]
Apply Eugene's [PLATFORM] Tone of Voice Profile.

Content Requirements:
- Cite specific permanent notes in [brackets] throughout
- Include Eugene's unique/contrarian perspectives
- Use concrete examples from knowledge base
- Connect to broader themes (dopamine, identity, Buddhism, AI, etc.)
- Avoid generic AI knowledge - only Eugene's original insights

Target: [800-2500] words (optimal for [PLATFORM])

Topic Details:
[Specific angles to cover, questions to answer, or frameworks to explore]
```

### Platform-Specific Prompts

**LinkedIn Article:**
```
Create a LinkedIn article (800-1200 words) about [TOPIC].

Hook: Start with a professional anecdote or surprising insight
Tone: Professional but accessible (Eugene's LinkedIn voice)
Structure: Problem → Insight → Evidence → Application
CTA: Thought-provoking question for comments

Read Eugene_LinkedIn_Tone_of_Voice_Profile.md first.
Cite permanent notes. Target 1,000 words.
```

**Medium Deep Dive:**
```
Create a comprehensive Medium article (1500-2500 words) about [TOPIC].

Hook: Compelling narrative opening
Tone: Depth-focused, intellectually rigorous
Structure: Multi-section analysis with extensive citations
Include: Counterarguments, nuance, implications

Target 2,000 words. Heavy permanent note citations.
```

**Substack Newsletter:**
```
Create a Substack newsletter (1000-2000 words) about [TOPIC].

Hook: Personal story or "here's what I've been thinking..."
Tone: Conversational, direct address ("you"), warm
Structure: 2-3 main insights with practical takeaways
CTA: Invite reader response/discussion

Target 1,500 words. Eugene's authentic voice.
```

## Article Metadata

Save with each article in ContentHub/Prepared/articles/:

```json
{
  "title": "Why Smart Companies Resist AI Adoption",
  "slug": "ai-adoption-barriers-2025-11-14",
  "topic": "AI agent adoption psychological barriers",
  "platform": "linkedin",
  "tone": "professional",
  "word_count": 1047,
  "read_time_minutes": 5,
  "created_at": "2025-11-14T14:45:00Z",
  "cornelius_session_id": "54da041a-a181-4e35-a4f3-5cfe8bfe7596",
  "cost_usd": 0.67,
  "cited_notes": [
    "AI adoption bottleneck is psychological not technical",
    "Professional identity creates AI resistance",
    "Finding a confirmation of the belief creates a spike of Dopamine"
  ],
  "status": "draft",
  "published_at": null,
  "post_urls": {}
}
```

## Use Cases

### 1. Regular Content Creation
```
User: "I need a LinkedIn article for this week"

Ruby:
/create-article "Recent insights on AI agent evolution" linkedin
# → Generate article
# → Review and approve
# → Post or schedule
```

### 2. Thought Leadership Series
```
# Create series on AI adoption
/create-article "Part 1: The psychology of AI resistance" linkedin
/create-article "Part 2: Overcoming identity attachment to AI" linkedin
/create-article "Part 3: Building AI-friendly organizational culture" linkedin

# Schedule weekly
```

### 3. Deep Dive Research
```
User: "Write comprehensive piece on dopamine and social media"

Ruby:
/create-article "The dopamine economy: How social media hijacks motivation" medium
# → 2,500-word deep dive
# → Heavy citation of permanent notes
# → Publish to Medium
```

### 4. Newsletter Content
```
User: "Create this week's newsletter"

Ruby:
/create-article "What I learned about AI agents this month" substack
# → Conversational newsletter style
# → Recent insights synthesized
# → Send to subscribers
```

## Performance Metrics

### Typical Generation
- **Time**: 15-30 seconds (depends on length)
- **Cost**: $0.50-0.80 (longer = more expensive)
- **Word count**: 800-2500 words
- **Quality**: High (synthesizes multiple permanent notes)

### Cost by Platform
- **LinkedIn** (1000 words): ~$0.50
- **Medium** (2000 words): ~$0.70
- **Substack** (1500 words): ~$0.60
- **Blog** (1800 words): ~$0.65

## Quality Indicators

### High-Quality Article (Generated by Cornelius)
✅ Cites 5-10+ specific permanent notes
✅ Includes Eugene's unique/contrarian perspectives
✅ Uses concrete examples from knowledge base
✅ Connects to broader themes (dopamine, Buddhism, AI)
✅ Authentic voice (not generic AI writing)
✅ Coherent narrative arc
✅ Actionable conclusion

### Low-Quality (Regenerate with Better Prompt)
❌ Generic AI knowledge (not from knowledge base)
❌ Few or no permanent note citations
❌ Surface-level analysis
❌ No contrarian or unique angles
❌ Lacks Eugene's voice
❌ Disjointed structure

## Editing Workflow

1. **Review Generated Article**
   - Check permanent note citations
   - Verify voice authenticity
   - Assess structure and flow

2. **Edit if Needed**
   - Use text editor or word processor
   - Maintain citation format [[ ]]
   - Preserve Eugene's voice

3. **Update Metadata**
   - Note any significant changes
   - Update word count if edited
   - Add edit timestamp

4. **Final Review**
   - Read aloud (voice check)
   - Verify all citations valid
   - Check platform-specific requirements

## Publishing Options

### Post to LinkedIn Now
```
/post-now linkedin text "[Article content from ContentHub/Prepared/articles/filename.md]"
```

### Schedule LinkedIn Article
```
/schedule-post "Monday 9am" linkedin text "[Article content]"
```

### Export for Medium/Substack
- Copy article from ContentHub/Prepared/articles/
- Paste into platform editor
- Format (Medium supports Markdown)
- Add images if needed
- Publish manually (no API for Medium/Substack)

## Integration Examples

### Example 1: Weekly LinkedIn Article
```
User: "Create and post this week's LinkedIn article"

Ruby:
1. /create-article "AI agents creating AI agents: Closed loop evolution" linkedin
2. Review generated article
3. /post-now linkedin text "[Generated article]"
4. Archive to ContentHub/Published/
```

### Example 2: Article Series
```
User: "Create 4-part series on AI adoption barriers"

Ruby:
1. /create-article "Part 1: The psychological bottleneck" linkedin
2. /create-article "Part 2: Identity and AI resistance" linkedin
3. /create-article "Part 3: Organizational transformation" linkedin
4. /create-article "Part 4: Building AI-friendly culture" linkedin

5. Schedule series (weekly):
   /schedule-post "Monday 9am" linkedin text "[Part 1]"
   /schedule-post "next Monday 9am" linkedin text "[Part 2]"
   ...
```

### Example 3: Cross-Platform Publishing
```
User: "Write about dopamine and post everywhere"

Ruby:
1. /create-article "The dopamine economy" linkedin
   # → 1,000-word LinkedIn version

2. /create-article "The dopamine economy" medium
   # → 2,000-word Medium version (more depth)

3. Post LinkedIn version:
   /post-now linkedin text "[LinkedIn article]"

4. Export Medium version:
   "Here's the Medium version: [ContentHub/Prepared/articles/dopamine-economy-medium.md]"
   "Copy and publish manually to Medium"
```

## Debugging

### If Article is Too Generic
- Add "Cite specific permanent notes" to prompt
- Request "Eugene's unique perspective, not general AI knowledge"
- Specify contrarian or non-obvious angles
- Reference specific note clusters (Buddhism, dopamine, AI)

### If Article Lacks Structure
- Provide explicit structure in prompt
- Request section headers
- Specify intro → body → conclusion format
- Give word count per section

### If Voice is Off
- Ensure tone of voice profile referenced in prompt
- Request "Eugene's authentic voice"
- Provide example sentences from previous articles
- Regenerate with voice-focused prompt

## Notes

- Articles draw from 1,883 notes, 550 permanent notes, 102 AI insights
- Best results cite 5-10+ permanent notes
- Longer articles cost more but provide deeper synthesis
- Session logs: `~/.claude/debug/<session-id>.txt`
- Can request multiple drafts (different angles) and choose best

## Future Enhancements (Not Yet Implemented)

- Auto-suggest article topics from recent insights
- Multi-draft generation (A/B test different angles)
- SEO optimization for blog posts
- Auto-image selection from knowledge base
- Citation linking to Obsidian vault
- Version control for edits
- Analytics integration (track performance)

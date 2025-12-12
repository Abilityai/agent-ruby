---
description: Get [User]'s perspective from knowledge base via Cornelius
---

# Get Perspective Command

Call Cornelius in headless mode to extract [User]'s unique perspective on a topic from his knowledge base (1,883 notes, 550 permanent notes, 102 AI insights).

## Usage

```
/get-perspective <topic or question>
```

## Parameters

- **topic or question**: What perspective to retrieve
  - Can be specific topic: "AI agent adoption barriers"
  - Can be question: "Why do companies resist AI adoption?"
  - Can be comparison: "Difference between dopamine and flow states"
  - Can be application: "How does Buddhism relate to AI design?"

## Examples

### Get Perspective on Topic
```
/get-perspective AI agent adoption barriers
```

### Ask Question
```
/get-perspective Why do smart people struggle with AI adoption?
```

### Get Contrarian View
```
/get-perspective What's the contrarian take on AI replacing jobs?
```

### Find Connections
```
/get-perspective How do dopamine, social media, and AI agent design relate?
```

## Workflow

1. **Format Prompt for Cornelius**
   - Structure request to get specific, actionable insights
   - Ask for relevant permanent note citations
   - Request [User]'s unique angle (not generic AI response)

2. **Call Cornelius (Headless Mode)**
   ```bash
   cd $CORNELIUS_AGENT_DIR
   claude -p "What's [User]'s unique perspective on [topic]? Cite specific permanent notes from the knowledge base. Focus on contrarian or non-obvious insights." --output-format json --timeout 60000
   ```

3. **Parse Response**
   - Extract result text from JSON response
   - Note session_id for debugging
   - Track cost (~$0.30-0.40 per call)

4. **Present to User**
   - Show [User]'s perspective
   - List cited notes (if provided)
   - Show cost and session info

5. **Cache Response** (optional)
   - Save to ContentHub/Prepared/ if will be used for content
   - Include metadata: topic, timestamp, cited notes, cost

## Response Format

```
🧠 [User]'s Perspective: [Topic]

[Cornelius's response with [User]'s unique insights and perspectives]

📝 Cited Notes:
- [[Note Title 1]] - Relevance explanation
- [[Note Title 2]] - Relevance explanation

💰 Cost: $0.34
⏱️ Response time: 5.6 seconds
🆔 Session: 54da041a-a181-4e35-a4f3-5cfe8bfe7596

---
Use this perspective to create content with /create-video or /post-now
```

## Headless Mode Details

### Command Pattern
```bash
cd $CORNELIUS_AGENT_DIR && \
claude -p "prompt here" --output-format json
```

### Response Structure
```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 5640,
  "result": "Cornelius's text response",
  "session_id": "uuid",
  "total_cost_usd": 0.34,
  "usage": {
    "input_tokens": 2,
    "cache_creation_input_tokens": 87012,
    "output_tokens": 56
  }
}
```

### Error Handling
```bash
# Check if error
if [ "$is_error" = "true" ]; then
  echo "Error from Cornelius: $result"
  exit 1
fi

# Extract result
perspective=$(echo "$response" | jq -r '.result')
cost=$(echo "$response" | jq -r '.total_cost_usd')
session_id=$(echo "$response" | jq -r '.session_id')
```

## Prompt Engineering for Cornelius

### Good Prompts (Specific, Actionable)
✅ "What's [User]'s unique perspective on AI adoption barriers? Focus on psychological factors and cite permanent notes about dopamine, identity, or belief systems."

✅ "Find connections between [User]'s notes on Buddhism, neuroscience, and AI agent design. What non-obvious insights emerge?"

✅ "What contrarian views does [User] have on AI replacing jobs? Look for insights that challenge conventional wisdom."

### Weak Prompts (Generic, Vague)
❌ "Tell me about AI adoption"
❌ "What does [User] think?"
❌ "Summarize the knowledge base"

### Prompt Templates

**For Content Creation:**
```
"What's [User]'s unique perspective on [TOPIC]? Provide:
1. Contrarian or non-obvious insight
2. Concrete examples from permanent notes
3. Connection to broader themes (dopamine, identity, Buddhism)
Format for use in a [LinkedIn post / video script / article]."
```

**For Finding Connections:**
```
"Find connections between [CONCEPT A] and [CONCEPT B] in [User]'s knowledge base. What non-obvious relationships exist? Cite specific permanent notes that bridge these concepts."
```

**For Contrarian Takes:**
```
"What's [User]'s contrarian perspective on [CONVENTIONAL WISDOM]? Look for permanent notes that challenge mainstream thinking. Explain the reasoning and evidence."
```

## Use Cases

### 1. Pre-Post Research
```
User: "I want to post about AI adoption"

Ruby:
/get-perspective AI adoption psychological barriers
# → Get [User]'s unique insights
# → Use in content creation
```

### 2. Video Script Foundation
```
User: "/create-video about AI adoption"

Ruby:
1. /get-perspective AI adoption barriers
2. Use perspective to generate 30-second script
3. Create HeyGen video
4. Post to platforms
```

### 3. Article Ideation
```
User: "What should I write about this week?"

Ruby:
/get-perspective What unique AI insights from recent notes would make compelling content?
# → Get suggestions from Cornelius
# → Present options to user
```

### 4. Connection Discovery
```
User: "How does my work on Buddhism relate to AI?"

Ruby:
/get-perspective connections between Buddhism and AI agent design
# → Get non-obvious bridges
# → Use for synthesis article
```

## Performance Metrics

### Typical Response
- **Time**: 5-6 seconds
- **Cost**: $0.30-0.40
- **Cache efficiency**: High on subsequent calls about similar topics
- **Context size**: 80K-100K+ tokens (full knowledge base loaded)

### Optimization Tips
- **Batch requests**: If need multiple perspectives, call once with combined prompt
- **Cache results**: Save responses for reuse in content
- **Specific prompts**: Reduce cost by being precise (less token usage)
- **Monitor costs**: Track monthly Cornelius call expenses

## Debugging

### If Response is Generic
- Check prompt specificity
- Add "Cite specific permanent notes" to prompt
- Request "[User]'s unique perspective, not general AI knowledge"

### If Response is Slow (>10 seconds)
- Knowledge base is large (1,883 notes)
- Normal for first call (cache building)
- Subsequent calls faster (cache hits)

### If Error Occurs
- Check session log: `~/.claude/debug/<session-id>.txt`
- Verify Cornelius is accessible
- Try simpler prompt
- Check if Cornelius agent is busy

## Integration Examples

### Example 1: Create Content from Perspective
```bash
# Get perspective
response=$(cd $CORNELIUS_AGENT_DIR && \
  claude -p "[User]'s unique perspective on AI adoption barriers" \
  --output-format json)

perspective=$(echo "$response" | jq -r '.result')

# Use in post
/post-now linkedin text "$perspective

#AI #AgentAdoption #Psychology"
```

### Example 2: Video with Perspective
```bash
# Get perspective
/get-perspective Why do companies resist AI agents?

# Response: [Detailed perspective about psychological barriers...]

# Create video
/create-video "Script: Companies resist AI because it threatens professional identity. Here's the psychology..." instagram,linkedin
```

### Example 3: Series of Perspectives
```bash
# Get multiple perspectives for content calendar
/get-perspective 5 unique AI insights from recent notes suitable for LinkedIn

# Response: [5 distinct perspectives]

# Schedule series
/schedule-post "Monday 9am" linkedin text "[Perspective 1]"
/schedule-post "Wednesday 2pm" linkedin text "[Perspective 2]"
/schedule-post "Friday 11am" linkedin text "[Perspective 3]"
```

## Comparison: get-perspective vs create-article

| Feature | /get-perspective | /create-article |
|---------|------------------|-----------------|
| **Output** | Raw insights/perspective | Formatted article |
| **Length** | Brief (1-3 paragraphs) | Long-form (500-2000 words) |
| **Use Case** | Quick content ideas | Full articles |
| **Cost** | $0.30-0.40 | $0.50-0.80 |
| **Time** | 5-6 seconds | 15-30 seconds |
| **Format** | Unstructured | Structured (intro, body, conclusion) |

**Rule of Thumb**: Use /get-perspective for social posts and videos, /create-article for blog posts and long-form content.

## Notes

- Cornelius has 1,883 total notes, 550 permanent notes, 102 AI insights
- Knowledge base focuses on: Consciousness, Dopamine, Decision-Making, AI Agents, Buddhism, Flow States
- Best results come from specific prompts that request contrarian or non-obvious insights
- Always cite permanent notes in prompts to ensure grounding in knowledge base
- Session logs available at `~/.claude/debug/<session-id>.txt` for debugging

## Future Enhancements (Not Yet Implemented)

- Cache perspectives in local database
- Auto-suggest related topics
- Perspective quality scoring
- Multi-perspective comparison
- Automatic content generation from perspectives

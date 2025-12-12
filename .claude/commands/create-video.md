---
description: Generate HeyGen video, convert to vertical, and post
---

# Create Video Command

End-to-end video creation: Generate HeyGen avatar video → Convert to vertical → Upload → Post to platforms.

## Usage

```
/create-video <script or topic> <platforms>
```

## Parameters

- **script or topic**: Either provide full script or topic for Cornelius to create
  - Direct script: "Here's the script: [30-second script text]"
  - Topic: "Create video about AI adoption barriers"

- **platforms**: Where to post (instagram, tiktok, youtube, linkedin, etc.)
  - Vertical video optimized for: Instagram, TikTok, YouTube Shorts, LinkedIn

## Examples

### Video from Provided Script
```
/create-video "Script: AI agents are transforming how we work. Here's why companies resist adoption despite the benefits..." instagram,tiktok
```

### Video from Knowledge Base Topic
```
/create-video "Create video about [User]'s perspective on AI agent adoption barriers" instagram
```

### Video from Recent Insights
```
/create-video "Create video summarizing [User]'s latest AI insights from this month" linkedin,youtube
```

## Workflow

### 1. Script Generation (if needed)
If topic provided (not full script):
- Call Cornelius in headless mode
- Prompt: "Create a 30-second HeyGen video script about [topic]. Use [User]'s unique perspectives from the knowledge base. Follow this structure: Hook (5s) → Insight (20s) → CTA (5s)."
- Receive script from Cornelius

### 2. HeyGen Video Generation
- **Avatar**: `d682534004b0414f86a32c812695cc83` (striped shirt, coworking) - BEST QUALITY
- **Voice**: `34971779749d4cb5bf36f1e67a2a6fc6` (casual, conversational) - MANDATORY PAIRING
- **Script**: Max 30 seconds (HeyGen limit)
- Generate via HeyGen API
- Poll for completion (~30-60 seconds)
- Get video URL (horizontal format)

### 3. Download HeyGen Video
- Download from HeyGen URL to local temp
- Prepare for conversion

### 4. Upload to Cloudinary
- Upload horizontal video to Cloudinary
- Get permanent public URL
- Use for Creatomate input

### 5. Convert to Vertical (Creatomate)
- **Mode**: Crop (default) or blur-pad
  - Crop: Crops horizontal to vertical 1080x1920
  - Blur-pad: Blurs edges, centers video
- **Captions**: Yellow karaoke (default) - word-by-word highlighting
  - Alternative: Compact subtitles
- Input: Cloudinary URL of horizontal video
- Output: Vertical video URL from Creatomate

### 6. Download & Upload Final Video
- Download converted vertical video
- Upload final video to Cloudinary
- Get permanent public URL for posting

### 7. Post to Platforms
- Use social-media-manager sub-agent
- Post via Blotato API to specified platforms
- Use video URL from Cloudinary

### 8. Archive & Confirm
- Save metadata to ContentHub/Published/
- Include: Script, HeyGen URL, Cloudinary URLs, post URLs
- Confirm to user with all links

## Avatar & Voice Configuration

### Primary Avatar (RECOMMENDED)
- **ID**: `d682534004b0414f86a32c812695cc83`
- **Description**: Sitting in striped shirt, coworking space
- **Quality**: 8/10 ⭐ BEST
- **MANDATORY Voice**: `34971779749d4cb5bf36f1e67a2a6fc6` (casual, conversational)

### Alternative Avatars (Lower Quality)
- `a2d4d1f5a4064ba099370dbc91fb80e1` - Black shorts (6/10)
- `219661545ed74aa5be9036c310cebb07` - Table, studio (6/10)
- `739854ac2b5748e09f41e2719e83ec3f` - Black shirt, podcast (6/10)

### Voice Options
- `34971779749d4cb5bf36f1e67a2a6fc6` - Casual, conversational (DEFAULT)
- `0f15fbc688e54d91936a4ed9b8085c73` - Professional, authoritative

## Script Guidelines (30 Seconds Max)

### Structure
1. **Hook (5 seconds)**: Attention-grabbing question or statement
2. **Insight (20 seconds)**: [User]'s unique perspective or contrarian take
3. **CTA (5 seconds)**: Call to action or thought-provoking conclusion

### Example Script
```
Hook: "Why do smart companies resist AI agents?"

Insight: "It's not technical - it's psychological. Admitting AI is better at parts of your job threatens your professional identity. That threat triggers dopamine-reinforced resistance. Companies say they want AI, but subconsciously they're protecting the status quo."

CTA: "Understanding this psychology is the first step to adoption."
```

### Writing Tips
- **Concise**: Max 30 seconds when read naturally
- **Conversational**: Write how [User] speaks, not academic
- **Contrarian**: Highlight unexpected angles from knowledge base
- **Actionable**: Give viewers something to think about

## Cost Tracking

Track per video:
- **Cornelius call** (if script generation): ~$0.30-0.40
- **HeyGen generation**: ~$0.10 per video
- **Creatomate conversion**: ~$0.05 per video
- **Cloudinary storage**: Minimal
- **Total**: ~$0.45-0.55 per video

## Error Handling

### HeyGen Fails
- Retry once with same script
- If fails again, suggest text post with script
- Log error details

### Creatomate Conversion Fails
- Retry with blur-pad mode if crop failed
- Try without captions if caption generation fails
- As last resort, post horizontal video to YouTube/LinkedIn

### Upload Fails
- Retry Cloudinary upload
- Check file size limits
- Suggest manual upload if persistent

### Posting Fails
- Save video to ContentHub/Prepared/
- Provide download link to user
- Suggest manual posting

## Platform-Specific Notes

### Instagram
- Requires 1080x1920 vertical
- Max 60 seconds (HeyGen is 30s, perfect fit)
- Use karaoke captions (high engagement)

### TikTok
- Vertical format essential
- Captions increase watch time
- First 3 seconds critical (strong hook)

### YouTube Shorts
- 1080x1920 vertical
- Max 60 seconds
- Captions helpful for silent viewing

### LinkedIn
- Accepts both horizontal and vertical
- Vertical gets higher engagement on mobile
- Professional tone important

## Example Full Workflow

```
User: /create-video "[User]'s perspective on AI adoption barriers" instagram,linkedin

Ruby:
1. Calls Cornelius: "Create 30-second script on AI adoption barriers"
2. Cornelius returns: "[Script about psychological resistance]"
3. Generates HeyGen video (avatar d6825..., voice 34971...)
4. Waits ~45 seconds for HeyGen completion
5. Downloads horizontal video
6. Uploads to Cloudinary → URL1
7. Sends URL1 to Creatomate (crop + yellow karaoke)
8. Receives vertical video URL from Creatomate
9. Downloads vertical video
10. Uploads final to Cloudinary → URL2
11. Posts URL2 to Instagram and LinkedIn via Blotato
12. Archives metadata + all URLs
13. Confirms to user:
    "✅ Video created and posted!

    Instagram: [post URL]
    LinkedIn: [post URL]

    Video URLs:
    - HeyGen: [URL]
    - Horizontal: [Cloudinary URL1]
    - Vertical: [Cloudinary URL2]

    Script used:
    [Script text]

    Total cost: $0.50"
```

## Performance Tips

- **Batch scripts**: If making multiple videos, generate scripts first, then process videos
- **Cache assets**: Reuse common backgrounds or overlays
- **Monitor costs**: Track HeyGen/Creatomate usage monthly
- **Quality check**: Preview video before posting if time-sensitive

## Future Enhancements (Not Yet Implemented)

- Automatic background music selection
- Custom branding overlays
- Multi-language caption generation
- A/B testing different hooks
- Automated thumbnail generation
- Series/batch video creation

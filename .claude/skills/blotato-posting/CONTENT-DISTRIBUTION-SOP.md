# Content Distribution SOP
**Standard Operating Procedure for Publishing Generated Content**

## Overview
This SOP applies to any "Generated Content" folder containing social media posts. Follow these instructions to distribute content across platforms efficiently.

⚠️ **CRITICAL**: Twitter has a **MAXIMUM 4 IMAGES PER TWEET** limit. Always check image count before including Twitter in carousel posts. For carousels with >4 images, use `linkedin,instagram,threads` instead.

---

## File Type Mapping

### 1. Text Posts (`text_post_*.md`)
**Platforms:** Twitter, LinkedIn, Threads, Bluesky, Facebook
**Method:** Blotato API (immediate or scheduled)
**Character Limits:**
- Twitter: 280 characters
- LinkedIn: 3000 characters
- Threads: 500 characters (strictly enforced)
- Bluesky: ~300 characters
- Facebook: No practical limit

**Command:**
```bash
bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/post.sh \
  "CONTENT_HERE" \
  "twitter,linkedin,threads" \
  "2025-10-29T14:00:00Z"  # Optional: for scheduling
```

---

### 2. LinkedIn Posts (`linkedin_post_*.md`)
**Platform:** LinkedIn only
**Method:** Blotato API
**Limit:** 3000 characters

**Command:**
```bash
bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/post.sh \
  "CONTENT_HERE" \
  "linkedin" \
  "2025-10-29T14:00:00Z"  # Optional
```

---

### 3. Twitter Threads (`twitter_thread_*.md`)
**Platform:** Twitter only
**Method:** Manual (Blotato doesn't support thread posting via API)
**Action Required:**
1. Read the thread file
2. Copy content
3. Post manually via Twitter interface or use Twitter API directly

**Alternative:** Break into individual tweets and schedule separately

---

### 4. Community Posts (`community_post_*.md`)
**Platforms:** LinkedIn, Facebook Groups
**Method:** Blotato API
**Note:** Community-style content, conversational tone

**Command:**
```bash
bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/post.sh \
  "CONTENT_HERE" \
  "linkedin,facebook"
```

---

### 5. Newsletter Content (`newsletter_*.md`)
**Platform:** Email / Newsletter platforms (Substack, Mailchimp, etc.)
**Method:** Manual or platform-specific API
**Action Required:**
1. Read newsletter file
2. Copy to newsletter platform
3. Schedule/publish through that platform

**Not supported by Blotato API**

---

### 6. LinkedIn Carousels (`linkedin_carousel_*.pdf` + `linkedin_carousel_text_*`)
**Platform:** LinkedIn only
**Method:** Manual (NOT supported by Blotato API - on roadmap)

**Current Limitation:** LinkedIn carousel posts via API require sponsored posts (paid ads)

**Action Required:**
1. Download the PDF file
2. Upload manually via LinkedIn web interface
3. Use the corresponding text file for the post caption

**Workaround Option:**
- Convert PDF pages to individual JPG/PNG images
- Post as multi-image post via Blotato (if supported)

---

## Standard Workflow

### For Any "Generated Content" Folder:

1. **Inventory the files:**
   ```bash
   ls -la "path/to/Generated Content/"
   ```

2. **Identify file types:**
   - Count text posts
   - Count LinkedIn posts
   - Count Twitter threads
   - Check for carousels (PDFs)
   - Check for newsletters

3. **Prioritize distribution:**
   - **Automated (Blotato API):** text_post, linkedin_post, community_post
   - **Manual Required:** twitter_thread, newsletter, linkedin_carousel

4. **Schedule automated posts:**
   - Space out posts by 2-4 hours
   - Use different times of day for variety
   - Convert times to ISO 8601 format (UTC)

5. **Handle manual posts:**
   - Create checklist for manual distribution
   - Note which platforms/posts need manual work

---

## Time Scheduling Guidelines

**Best posting times (convert to UTC):**
- **Morning:** 9:00 AM local → schedule for high engagement
- **Afternoon:** 2:00 PM local → mid-day break browsing
- **Evening:** 6:00 PM local → after-work browsing

**Spacing between posts:**
- Minimum 2 hours between posts
- Ideal 3-4 hours for different audience segments

**ISO 8601 format examples:**
```
2025-10-29T09:00:00Z  # 9 AM UTC
2025-10-29T14:00:00Z  # 2 PM UTC
2025-10-29T18:00:00Z  # 6 PM UTC
```

---

## Platform Selection Strategy

### Maximum Reach (Cross-Platform):
```bash
"twitter,linkedin,threads,bluesky"
```

### Professional Content:
```bash
"linkedin"
```

### Quick Updates / Casual:
```bash
"twitter,threads,bluesky"
```

### Community Building:
```bash
"linkedin,facebook"
```

---

## Automation Script Template

```bash
#!/bin/bash
# Distribution script for generated content folder

CONTENT_DIR="$1"
BASE_TIME="$2"  # e.g., "2025-10-29T14:00:00Z"

# Find all text posts
for file in "$CONTENT_DIR"/text_post_*.md; do
    CONTENT=$(cat "$file")
    # Schedule 2 hours apart
    bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/post.sh \
      "$CONTENT" \
      "twitter,linkedin" \
      "$BASE_TIME"
done

# Find LinkedIn-specific posts
for file in "$CONTENT_DIR"/linkedin_post_*.md; do
    CONTENT=$(cat "$file")
    bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/post.sh \
      "$CONTENT" \
      "linkedin" \
      "$BASE_TIME"
done
```

---

## Manual Distribution Checklist

For content requiring manual posting:

- [ ] **Twitter Threads**
  - [ ] Copy thread content
  - [ ] Post via Twitter interface
  - [ ] Verify thread continuity

- [ ] **LinkedIn Carousels**
  - [ ] Download PDF files
  - [ ] Upload via LinkedIn interface
  - [ ] Add caption from text file
  - [ ] Verify carousel display

- [ ] **Newsletters**
  - [ ] Copy newsletter content
  - [ ] Format in newsletter platform
  - [ ] Schedule publication
  - [ ] Verify email rendering

---

## Quick Reference

### Read content file:
```bash
cat "path/to/file.md"
```

### Post immediately:
```bash
bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/post.sh \
  "CONTENT" "twitter,linkedin"
```

### Schedule post:
```bash
bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/post.sh \
  "CONTENT" "twitter,linkedin" "2025-10-29T14:00:00Z"
```

### Upload media first:
```bash
bash $CORNELIUS_DIR/.claude/skills/blotato-posting/scripts/upload-media.sh \
  "/path/to/image.jpg" "image"
```

---

## Platform Image Limitations

### Twitter/X
- **MAXIMUM 4 IMAGES PER TWEET**
- This is a hard Twitter API limit, not a Blotato limitation
- For carousel posts with >4 images:
  - **Option 1**: Exclude Twitter from platform list
  - **Option 2**: Split into multiple tweets (images 1-4, then 5-8, etc.)
  - **Option 3**: Post first 4 images only
- **Always check image count before scheduling to Twitter**

### Other Platforms
- **LinkedIn**: Up to 9 images per carousel post
- **Instagram**: Up to 10 images per carousel post
- **Threads**: Up to 10 images per post
- **Facebook**: Up to 10 images per post

### Carousel Strategy
When distributing carousel content:
- 4 images or less: Include all platforms including Twitter
- 5-10 images: Use `linkedin,instagram,threads` (exclude Twitter)
- More than 10 images: Split carousel or manually post to LinkedIn

## Limitations & Workarounds

| Content Type | Limitation | Workaround |
|--------------|-----------|------------|
| Twitter Carousels | Max 4 images per tweet | Exclude Twitter OR split into multiple tweets |
| Twitter Threads | No API support | Manual posting or individual tweets |
| LinkedIn Carousels | No API support (PDFs) | Manual upload or convert to images |
| Newsletters | Platform-specific | Use platform's native API/interface |
| Instagram | Requires media | Upload image first, then post |
| YouTube | Complex metadata | Use YouTube API directly |

---

## Success Checklist

After distributing content from a folder:

- [ ] All text posts scheduled/posted
- [ ] All LinkedIn posts scheduled/posted
- [ ] All community posts scheduled/posted
- [ ] Manual posts documented for follow-up
- [ ] Posting times spaced appropriately
- [ ] Confirmation IDs captured for tracking
- [ ] Manual distribution checklist created for remaining items

---

## Notes

- Always verify content length against platform limits
- Check Blotato dashboard for scheduled posts: https://www.blotato.com/
- Rate limits: 30 posts/minute (publishing), 10 uploads/minute (media)
- API key location: `$CORNELIUS_DIR/.claude/skills/blotato-posting/config.json`
- Blotato docs: https://help.blotato.com/api/start

---

**Last Updated:** 2025-11-21 - Added Twitter 4-image carousel limit

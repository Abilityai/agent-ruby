# Schedule Content Command

You are helping the user schedule social media content from a "Generated Content" folder following the Content Distribution SOP.

## Your Task

1. **Ask for content folder path** (or detect if user provided it)
   - Example: `[User] Personal Brand/Content/10.2025/Context_Rot_published/Generated Content`

2. **Analyze the folder contents:**
   - List all files found
   - Categorize by type:
     - `text_post_*.md` - Short cross-platform posts
     - `linkedin_post_*.md` - LinkedIn long-form posts
     - `community_post_*.md` - Community engagement posts
     - `twitter_thread_*.md` - Twitter threads (manual)
     - `linkedin_carousel_*.pdf` + `linkedin_carousel_text_*` - LinkedIn carousels (manual)
     - `newsletter_*.md` - Email newsletters (manual)

3. **Read and preview content:**
   - Read the first few lines of each file
   - Show the user what content will be scheduled

4. **Propose scheduling plan:**
   - Calculate times starting from "today at X PM" or user-specified time
   - Space posts 2-4 hours apart
   - Suggest appropriate platforms for each post type
   - Convert times to ISO 8601 UTC format
   - Show the complete schedule in a table format

5. **Present to user for confirmation:**
   ```
   PROPOSED SCHEDULE:

   📅 Automated Posts (via Blotato API):

   | Time | Platforms | Content Preview |
   |------|-----------|----------------|
   | 2 PM | Twitter, LinkedIn | "Your AI model has a personality..." |
   | 4 PM | LinkedIn | "The biggest mistake people make..." |

   ⚠️ Manual Posts Required:
   - 2 LinkedIn Carousels (PDFs) - Post via LinkedIn UI
   - 1 Twitter Thread - Post manually or as separate tweets
   - 2 Newsletters - Use email platform

   ⚠️ Twitter Carousel Limitation:
   - Twitter allows MAX 4 images per tweet
   - Carousels with >4 images: Split into multiple tweets or exclude Twitter

   Ready to schedule these posts? (yes/no)
   ```

6. **After user confirms "yes":**
   - Execute the bash commands to schedule each post
   - Capture and display the submission IDs
   - **Update `.claude/memory/schedule.json`** with all scheduled posts
   - Create a summary of scheduled posts
   - Remind user about manual posts

7. **Provide post-scheduling summary:**
   ```
   ✅ SCHEDULED SUCCESSFULLY:

   - 3 posts scheduled via Blotato
   - Submission IDs: [list them]
   - Added to schedule tracker: .claude/memory/schedule.json
   - View scheduled posts: https://my.blotato.com/queue/schedules

   📋 MANUAL POSTING CHECKLIST:
   - [ ] Upload 2 LinkedIn Carousels
   - [ ] Post Twitter thread
   - [ ] Schedule 2 newsletters
   ```

## Reference SOP

The full Content Distribution SOP is located at:
`$VAULT_BASE_PATH/.claude/skills/blotato-posting/CONTENT-DISTRIBUTION-SOP.md`

Read this file for detailed instructions on:
- File type mappings
- Platform capabilities
- Scheduling guidelines
- Command syntax

## Scheduling Script Location

Use this script for posting:
```bash
bash $VAULT_BASE_PATH/.claude/skills/blotato-posting/scripts/post.sh \
  "CONTENT" \
  "platforms" \
  "ISO_8601_TIME"
```

## Important Notes

- Always convert times to ISO 8601 UTC format (e.g., `2025-10-29T14:00:00Z`)
- Get current date/time first: `date '+%Y-%m-%d %H:%M:%S %Z'`
- Space posts at least 2 hours apart
- Default platforms for text posts: `twitter,linkedin`
- Default platforms for LinkedIn posts: `linkedin` only
- Never post immediately without user confirmation

### Twitter Image Carousel Limitation
- **Twitter allows MAXIMUM 4 images per tweet**
- When scheduling carousel posts:
  - If carousel has ≤4 images: Include Twitter in platforms
  - If carousel has >4 images: Exclude Twitter OR split into multiple tweets
- Always check image count before scheduling to Twitter
- For 10-slide carousels: Schedule to LinkedIn/Instagram/Threads, exclude Twitter

## Schedule Tracker

After scheduling posts via Blotato, update `.claude/memory/schedule.json` with:
- Post ID (unique identifier)
- Scheduled time (ISO 8601 UTC)
- Platforms and account IDs
- Content text and media URLs
- Blotato submission IDs
- Status: "scheduled"

This allows tracking what's scheduled without needing Blotato API access.

## Workflow Summary

1. Ask for folder path
2. Analyze files (list, categorize, read previews)
3. Propose schedule (table format with times, platforms, previews)
4. Get user confirmation
5. Execute scheduling commands
6. **Update .claude/memory/schedule.json** with all entries
7. Display submission IDs and manual checklist
8. Remind user to check Blotato dashboard

---
description: Schedule content for future posting
---

# Schedule Post Command

Schedule content to be posted at a specific future date and time across social platforms.

## Usage

```
/schedule-post <date/time> <platforms> <content type> <content>
```

## Parameters

- **date/time**: Natural language or ISO format
  - "tomorrow at 9am"
  - "next Monday 2pm"
  - "2025-11-20T09:00:00Z"
  - Converts to UTC ISO 8601 for Blotato API

- **platforms**: Comma-separated list or "all"
  - linkedin, twitter, instagram, tiktok, youtube, threads, facebook, bluesky, pinterest

- **content type**: text | image | video | carousel
  - **Note**: Twitter supports MAX 4 images per tweet
  - For carousels with >4 images, exclude Twitter from platforms

- **content**: Post text + media path/URL (if applicable)

## Examples

### Schedule LinkedIn Post for Tomorrow
```
/schedule-post "tomorrow at 9am" linkedin text "New article on AI agent adoption patterns"
```

### Schedule Video Across Platforms Next Week
```
/schedule-post "next Monday 2pm" instagram,tiktok video "AI insights video" /path/to/video.mp4
```

### Schedule Week of Content
```
/schedule-post "Monday 9am" linkedin text "Post 1 content"
/schedule-post "Wednesday 2pm" linkedin text "Post 2 content"
/schedule-post "Friday 11am" linkedin text "Post 3 content"
```

### Schedule Carousel (10 Slides - Exclude Twitter)
```
/schedule-post "tomorrow 2pm" "linkedin,instagram,threads" carousel "Carousel post text" /path/to/carousel/
```
**Note**: Excluded Twitter because carousel has 10 images (Twitter max is 4)

## Workflow

1. **Parse Date/Time**
   - Convert natural language to UTC ISO 8601
   - Validate future date (not in past)
   - Calculate timezone offset

2. **Read Tone of Voice Profile**
   - Apply appropriate profile for each platform
   - Ensure brand consistency

3. **Prepare Media** (if applicable)
   - Upload to Cloudinary if needed
   - Store permanent URL

4. **Schedule via Blotato**
   - Call Blotato schedule API
   - Get scheduled post ID(s)
   - Store submission details

5. **Update Schedule Tracker**
   - Add entry to `.claude/memory/schedule.json`
   - Include all post details (see structure below)
   - Update metadata counters

6. **Confirm to User**
   - Show scheduled time (user's timezone)
   - List platforms
   - Provide instructions to view/edit in Blotato dashboard

## Schedule Tracker Entry Structure

Each scheduled post is added to `.claude/memory/schedule.json`:

```json
{
  "id": "post-2025-11-20-linkedin-twitter",
  "created_at": "2025-11-15T18:00:00Z",
  "scheduled_time": "2025-11-20T09:00:00Z",
  "platforms": ["linkedin", "twitter"],
  "account_ids": {"linkedin": "4180", "twitter": "4790"},
  "content_type": "text|video|image",
  "content_text": "Post text content",
  "media_file": "/path/to/file.mp4",
  "media_url": "https://res.cloudinary.com/...",
  "blotato_submission_ids": {"linkedin": "sub_123", "twitter": "sub_456"},
  "status": "scheduled|posted|failed",
  "updated_at": "2025-11-15T18:00:00Z"
}
```

## Time Zone Handling

- **Input**: Accept user's local time or UTC
- **Storage**: Store as UTC ISO 8601
- **Display**: Show user's local time in confirmation
- **Blotato**: Send UTC ISO 8601 format

## Scheduling Best Practices

### LinkedIn
- Monday-Friday: 9am-11am, 12pm-2pm, 5pm-6pm
- Avoid weekends

### Twitter/X
- Daily: 9am-11am, 12pm-1pm, 5pm-6pm
- High engagement during work hours

### Instagram
- Daily: 11am-1pm, 7pm-9pm
- Visual content performs best evenings

### TikTok
- Daily: 6am-10am, 7pm-11pm
- Peak during commute and evening hours

## Managing Scheduled Posts

### View Schedule
- Local tracker: `.claude/memory/schedule.json`
- Blotato dashboard: https://my.blotato.com/queue/schedules

### Edit Scheduled Post
- Must edit directly in Blotato dashboard (API limitation)
- Update local tracker manually if changed

### Cancel Scheduled Post
- Cancel in Blotato dashboard
- Update local tracker: change status to "canceled"

### Update Posted Status
- After Blotato posts content, manually update tracker
- Change status from "scheduled" to "posted"
- Update `updated_at` timestamp

## Configuration

Uses same Blotato API configuration as /post-now:
`Ruby/.claude/skills/blotato-posting/config.json`

## Platform Limitations

### Twitter/X
- **Maximum 4 images per tweet**
- When scheduling carousels with >4 images:
  - Option 1: Exclude Twitter from platforms
  - Option 2: Split into multiple tweets (first 4 images, then remaining)
  - Option 3: Create thread with images distributed across tweets
- Always check image count before including Twitter in carousel posts

### Other Platform Limits
- LinkedIn: Up to 9 images per carousel post
- Instagram: Up to 10 images per carousel post
- Threads: Up to 10 images per post

## Error Handling

- **Invalid date**: Prompt user to clarify
- **Past date**: Error, request future date
- **Media upload fails**: Save draft, notify user
- **Schedule API error**: Save to Prepared/, suggest manual schedule
- **Rate limit**: Queue for later, notify user
- **Too many images for Twitter**: Warn user, suggest excluding Twitter or splitting

## Notes

- Scheduled posts can be edited in Blotato dashboard
- Time zone conversions use user's system timezone
- Maximum scheduling window depends on Blotato plan
- Can schedule up to 30 days in advance (typical limit)

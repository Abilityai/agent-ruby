# Ruby Schedule Tracker

This directory contains Ruby's local schedule tracking system.

## Files

### `schedule.json`
Main schedule tracker file that mirrors Blotato's scheduling queue.

**Why we need this:**
- Blotato API doesn't provide GET endpoints to query scheduled posts
- This local tracker allows Ruby to know what's scheduled without dashboard access
- Provides a single source of truth for scheduled content

## Usage

### When Scheduling a Post

1. Schedule via Blotato API (via `/schedule-post` or `/schedule-prepared-content`)
2. Capture the `postSubmissionId` from Blotato response
3. Add entry to `schedule.json`:

```json
{
  "id": "post-2025-11-20-linkedin-twitter",
  "created_at": "2025-11-15T18:00:00Z",
  "scheduled_time": "2025-11-20T09:00:00Z",
  "platforms": ["linkedin", "twitter"],
  "account_ids": {"linkedin": "4180", "twitter": "4790"},
  "content_type": "text",
  "content_text": "Your post content here",
  "media_file": null,
  "media_url": null,
  "blotato_submission_ids": {"linkedin": "sub_abc123", "twitter": "sub_xyz789"},
  "status": "scheduled",
  "updated_at": "2025-11-15T18:00:00Z"
}
```

4. Update metadata counters (`total_scheduled`)

### Checking What's Scheduled

Read `schedule.json` and filter by `status: "scheduled"` to see upcoming posts.

### After a Post Publishes

Manually update the entry:
- Change `status` from "scheduled" to "posted"
- Update `updated_at` timestamp
- Increment `metadata.total_posted`
- Decrement `metadata.total_scheduled`

### If a Post Fails

- Change `status` to "failed"
- Check Blotato dashboard for error details
- Update `updated_at` timestamp

### Canceling a Scheduled Post

1. Cancel in Blotato dashboard (API doesn't support cancellation)
2. Update local entry: `status: "canceled"`
3. Update `updated_at` timestamp

## Field Definitions

- **id**: Unique identifier (format: `post-YYYY-MM-DD-platform1-platform2`)
- **created_at**: When this schedule entry was created (ISO 8601 UTC)
- **scheduled_time**: When Blotato will post this content (ISO 8601 UTC)
- **platforms**: Array of platform names
- **account_ids**: Map of platform to Blotato account ID
- **content_type**: "text", "video", or "image"
- **content_text**: The actual post text content
- **media_file**: Local file path (if video/image)
- **media_url**: Cloudinary URL (if media was uploaded)
- **blotato_submission_ids**: Map of platform to Blotato submission ID
- **status**: "scheduled", "posted", "failed", or "canceled"
- **updated_at**: Last time this entry was modified (ISO 8601 UTC)

## Best Practices

1. **Always update after scheduling** - Keep the tracker in sync with Blotato
2. **Use consistent ID format** - Makes entries easy to find
3. **Update status after posts publish** - Keeps history accurate
4. **Don't delete old entries** - Keep for audit trail
5. **Verify Blotato dashboard** - This is a mirror, not the source of truth

## Troubleshooting

**Problem**: Tracker says "scheduled" but post already published
**Solution**: Check Blotato dashboard, update tracker status to "posted"

**Problem**: Can't find a scheduled post in tracker
**Solution**: Check Blotato dashboard, manually add entry if needed

**Problem**: Blotato submission ID missing
**Solution**: Check Blotato API response, update tracker with correct ID

## Integration

This tracker is automatically updated by:
- `/schedule-post` command
- `/schedule-prepared-content` command

Both commands will add entries after successfully scheduling via Blotato API.

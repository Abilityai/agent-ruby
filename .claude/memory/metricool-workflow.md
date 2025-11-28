# Metricool MCP Integration - Ruby Agent

## Overview

Metricool MCP server provides analytics and posting capabilities for all 5 platforms (Instagram, TikTok, YouTube, LinkedIn, Twitter/X).

**Status:** ✅ Installed and functional (as of 2025-01-24)

---

## Configuration

**Location:** `/Users/eugene/Dropbox/Agents/Ruby/.mcp.json:77-87`

```json
"mcp-metricool": {
  "command": "uvx",
  "args": ["--upgrade", "mcp-metricool"],
  "env": {
    "METRICOOL_USER_TOKEN": "JOLNVZOELZCJGEJXXXBXQGMAKWCXARCAQPUPVOABLGOEGVPRZAMGEWZXXERGDSVK",
    "METRICOOL_USER_ID": "4303579"
  }
}
```

**Installation Method:** Claude Code CLI
```bash
claude mcp add-json "mcp-metricool" '{...}'
```

---

## Account Details

**Brand:** Eugene+Vyborov
**Blog ID:** 5544767
**Timezone:** Europe/Lisbon

**Connected Platforms:**
- Instagram: @evyborov
- Twitter/X: @evyborov
- LinkedIn: Personal profile (urn:li:person:dQsbYqOk6Z)
- TikTok: @eugene.vyborov8
- YouTube: Channel UCU5fgVZhh3ss9FCRkLXtcdg

---

## Available Tools (28 Total)

### Analytics Queries

**Instagram:**
- `get_instagram_posts(init_date, end_date, blog_id)`
- `get_instagram_reels(init_date, end_date, blog_id)`
- `get_instagram_stories(init_date, end_date, blog_id)`

**TikTok:**
- `get_tiktok_videos(init_date, end_date, blog_id)`

**YouTube:**
- `get_youtube_videos(init_date, end_date, blog_id)`

**LinkedIn:**
- `get_linkedin_posts(init_date, end_date, blog_id)`

**Twitter/X:**
- `get_x_posts(init_date, end_date, blog_id)`

**Facebook:**
- `get_facebook_posts(init_date, end_date, blog_id)`
- `get_facebook_reels(init_date, end_date, blog_id)`
- `get_facebook_stories(init_date, end_date, blog_id)`

**Other Platforms:**
- `get_thread_posts()` - Threads
- `get_bluesky_posts()` - Bluesky
- `get_pinterest_pins()` - Pinterest
- `get_twitch_videos()` - Twitch

### Campaign Analytics

- `get_facebookads_campaigns()`
- `get_googleads_campaigns()`
- `get_tiktokads_campaigns()`

### Competitive Analysis

- `get_network_competitors(network, init_date, end_date, blog_id, limit, timezone)`
- `get_network_competitors_posts(network, init_date, end_date, blog_id, limit, timezone)`

**Supported networks:** twitter, facebook, instagram, youtube, twitch, bluesky

### Content Scheduling

- `post_schedule_post(date, blog_id, info)` - Schedule new post
- `get_scheduled_posts(blog_id, start, end, timezone, extendedRange)` - View scheduled
- `update_schedule_post(id, date, blog_id, info)` - Modify scheduled post
- `get_best_time_to_post(start, end, blog_id, provider, timezone)` - Optimal timing

### Pinterest Management

- `get_pinterest_boards(blog_id)` - List boards for pin posting

### Metrics & Analytics

- `get_metrics(network)` - Available metrics for platform
- `get_analytics(blog_id, start, end, timezone, network, metric)` - Custom metrics query

---

## Date Format Guide

**Instagram, LinkedIn, TikTok, Facebook, Threads, Bluesky, Pinterest, YouTube, Twitch:**
- Format: `YYYY-MM-DD`
- Example: `2025-01-24`

**Twitter/X:**
- Format: `YYYYMMDD` (no dashes)
- Example: `20250124`

**Timezone:**
- Format: URL-encoded (e.g., `Europe%2FLisbon`)
- Ruby's timezone: `Europe%2FLisbon`

---

## Usage Examples

### Get Best Time to Post

```python
get_best_time_to_post(
    start="2025-01-24",
    end="2025-01-31",
    blog_id=5544767,
    provider="linkedin",
    timezone="Europe%2FLisbon"
)
```

**Returns:** Engagement scores by day/hour

**Best LinkedIn Times (Based on Data):**
- Wednesday 11am (2790 score) 🔥
- Thursday 11am (2914 score) 🔥
- Friday 11am (2217 score)
- Tuesday 11am (2445 score)

### Get Recent Posts

```python
get_instagram_reels(
    init_date="2025-01-01",
    end_date="2025-01-24",
    blog_id=5544767
)
```

### Schedule a Post

```python
post_schedule_post(
    date="2025-01-25T11:00:00",
    blog_id=5544767,
    info={
        "text": "Post content here",
        "providers": [{"network": "linkedin"}],
        "publicationDate": {
            "dateTime": "2025-01-25T11:00:00",
            "timezone": "Europe/Lisbon"
        },
        "media": [],
        "autoPublish": True,
        "draft": False,
        # Network-specific data
        "linkedinData": {
            "type": "post",
            "previewIncluded": True
        }
    }
)
```

### Get Competitor Performance

```python
get_network_competitors(
    network="linkedin",
    init_date="2025-01-01",
    end_date="2025-01-24",
    blog_id=5544767,
    limit=10,
    timezone="Europe%2FLisbon"
)
```

---

## Data Availability Timeline

**Connected:** 2025-01-24

**Historical Backfill:**
- Expected: 24-48 hours after connection
- Typical range: Up to 2 months of historical data
- First check: 2025-01-26

**As of 2025-01-24:**
- ✅ Best time recommendations working
- ✅ Brand info retrieved
- ⏳ Post analytics pending (no data yet)
- ⚠️ Twitter API returning errors (may need reauth)

---

## Workflow Integration

### Current Strategy (Phase 1)

**Posting:** Continue using Blotato
**Analytics:** Use Metricool (after data backfills)

**Rationale:**
- Blotato is known working system for posting
- Metricool provides analytics Blotato lacks
- Best-of-breed approach until Metricool posting is tested

### Future Strategy (Phase 2)

After 2 weeks of data collection:
1. Analyze content performance via Metricool
2. Test Metricool posting for simple posts
3. Compare posting capabilities vs Blotato
4. Decide: consolidate to Metricool or keep both

---

## Known Limitations

### Platform API Restrictions

**Facebook:**
- Cannot publish carousel ads
- Cannot tag users/products
- Cannot add feelings to posts
- Cannot create polls

**Instagram:**
- Cannot edit published posts
- Cannot tag private accounts
- Cannot add GIFs
- Cannot sync story highlights

**Twitter/X:**
- Cannot post mixed media
- Cannot customize thumbnails

**LinkedIn:**
- Cannot publish articles
- Cannot customize author names
- Cannot create event posts

**TikTok:**
- Cannot add overlay text
- Cannot add filters
- Limited demographic reporting

**YouTube:**
- Cannot post community posts
- Cannot customize Shorts thumbnails

These are **platform limitations**, not Metricool - all third-party tools face these restrictions.

---

## Posting Structure Reference

### Network-Specific Data

**Twitter:**
```json
"twitterData": {
  "tags": [] // For image tagging, not hashtags
}
```

**Facebook:**
```json
"facebookData": {
  "type": "POST|REEL|STORY",
  "title": "Video title (separate from text)",
  "boost": 0.0,
  "boostPayer": "string",
  "boostBeneficiary": "string"
}
```

**Instagram:**
```json
"instagramData": {
  "type": "POST|REEL|STORY",
  "collaborators": [{"username": "string", "deleted": false}],
  "carouselTags": {
    "0": [{"username": "user", "x": 0.5, "y": 0.5}]
  },
  "showReelOnFeed": true,
  "boost": 0.0,
  "boostPayer": "string",
  "boostBeneficiary": "string"
}
```

**LinkedIn:**
```json
"linkedinData": {
  "documentTitle": "string",
  "publishImagesAsPDF": false,
  "previewIncluded": true,
  "type": "post|poll",
  "poll": {
    "question": "string",
    "options": [{"text": "option1"}, {"text": "option2"}],
    "settings": {"duration": "ONE_DAY|THREE_DAYS|SEVEN_DAYS|FOURTEEN_DAYS"}
  }
}
```

**Pinterest:**
```json
"pinterestData": {
  "boardId": "string",
  "pinTitle": "string",
  "pinLink": "string",
  "pinNewFormat": false
}
```

**YouTube:**
```json
"youtubeData": {
  "title": "string",
  "type": "video|short",
  "privacy": "public|unlisted|private",
  "tags": ["tag1", "tag2"],
  "category": "EDUCATION|SCIENCE_TECHNOLOGY|...",
  "madeForKids": false
}
```

**TikTok:**
```json
"tiktokData": {
  "disableComment": false,
  "disableDuet": false,
  "disableStitch": false,
  "privacyOption": "PUBLIC_TO_EVERYONE|MUTUAL_FOLLOW_FRIENDS|FOLLOWER_OF_CREATOR|SELF_ONLY",
  "commercialContentThirdParty": false,
  "commercialContentOwnBrand": false,
  "title": "string",
  "autoAddMusic": false,
  "photoCoverIndex": 0
}
```

**Bluesky:**
```json
"blueskyData": {
  "postLanguages": ["en", "pt"]
}
```

**Threads:**
```json
"threadsData": {
  "allowedCountryCodes": ["US", "PT"]
}
```

---

## Troubleshooting

### No Data Returned

**Cause:** Recently connected accounts
**Solution:** Wait 24-48 hours for backfill

### Twitter API Errors

**Cause:** May need re-authorization
**Solution:** Reconnect Twitter in Metricool dashboard

### Timezone Issues

**Fix:** Always use `Europe%2FLisbon` for Eugene's account

### MCP Not Loading

**Check:** `.mcp.json` configuration exists
**Restart:** Close and reopen Ruby agent
**Verify:** `claude mcp list` shows mcp-metricool

---

## Resources

- [Metricool MCP GitHub](https://github.com/metricool/mcp-metricool)
- [Metricool Help Center](https://help.metricool.com)
- [API Documentation](https://app.metricool.com/resources/apidocs/)
- [Installation Guide](https://help.metricool.com/en/article/install-and-set-up-the-metricool-mcp-in-claude-desktop-1i9v5ek/)

---

**Last Updated:** 2025-01-24
**Status:** ✅ Operational, pending historical data backfill

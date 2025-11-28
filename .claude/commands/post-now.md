---
description: Post content immediately to social platforms
---

# Post Now Command

Post content immediately to one or more social media platforms using Blotato API.

## Usage

```
/post-now <platforms> <content type> <content>
```

## Parameters

- **platforms**: Comma-separated list (e.g., "linkedin,twitter" or "all")
  - Options: linkedin, twitter, instagram, tiktok, youtube, threads, facebook, bluesky, pinterest
  - Special: "all" posts to all configured platforms

- **content type**: Type of post
  - "text" - Text-only post
  - "image" - Post with image
  - "video" - Post with video
  - "carousel" - Multiple images (Twitter: MAX 4, Instagram/LinkedIn: up to 10)

- **content**: The post content
  - For text posts: Provide the text content
  - For media posts: Provide text + media path/URL

## Examples

### Text Post to LinkedIn
```
/post-now linkedin text "Just published my thoughts on AI agent adoption: [link]"
```

### Image Post to Multiple Platforms
```
/post-now linkedin,twitter image "Check out this framework! 🚀" /path/to/image.png
```

### Video Post to Instagram
```
/post-now instagram video "New video on AI psychology" /path/to/video.mp4
```

### Post to All Platforms
```
/post-now all text "Excited to announce our new AI agent platform! 🎉"
```

## Workflow

1. **Read Tone of Voice Profile** (if applicable)
   - LinkedIn: Read Eugene_LinkedIn_Tone_of_Voice_Profile.md
   - Twitter: Read Eugene_Twitter_Tone_of_Voice_Profile.md
   - Threads: Read Eugene_Text_Post_Tone_of_Voice_Profile.md

2. **Prepare Media** (if applicable)
   - Upload to Cloudinary if local file
   - Get public URL for Blotato

3. **Format Content**
   - Apply platform-specific formatting
   - Optimize text length for platform
   - Add hashtags if appropriate

4. **Post via Blotato**
   - Use social-media-manager sub-agent
   - Call Blotato API with account IDs
   - Handle platform-specific requirements

5. **Archive Metadata**
   - Save to ContentHub/Published/
   - Include post URLs, timestamps, metadata

6. **Confirm to User**
   - Show post URLs
   - Confirm platforms posted
   - Display any errors

## Configuration

Uses Blotato API configuration from:
`Ruby/.claude/skills/blotato-posting/config.json`

Account IDs:
- YouTube: 8598
- Instagram: 9987
- LinkedIn: 4180
- Twitter: 4790
- Threads: 3435
- TikTok: 21395

## Error Handling

- **Media upload fails**: Retry once, then notify user
- **Blotato API error**: Log error, show user details
- **Platform-specific error**: Skip that platform, post to others
- **Rate limit**: Notify user, suggest scheduling instead

## Platform Limitations

### Twitter/X
- **Maximum 4 images per tweet**
- For carousel posts with >4 images:
  - Exclude Twitter from platforms OR
  - Split into multiple tweets
- Character limit: 280 (or 25,000 for long posts)
- Video posts may fail for large files (Blotato limitation)

### Instagram
- Requires 1080x1920 vertical video format
- Up to 10 images per carousel

### LinkedIn
- Up to 3000 characters
- Up to 9 images per carousel

### Threads
- Up to 500 characters (strictly enforced)
- Up to 10 images per post

### YouTube
- **CRITICAL**: Always specify privacy status when posting
  - `privacyStatus: "public"` - Public video (default if not specified)
  - `privacyStatus: "unlisted"` - Unlisted (only accessible via link)
  - `privacyStatus: "private"` - Private (only you can see)
- **IMPORTANT**: Never submit multiple times to correct privacy status - get it right the first time
- Requires: `title`, `privacyStatus`, `shouldNotifySubscribers`
- Video URLs from Dropbox/Google Drive can be used directly (no Cloudinary upload needed)

## Notes

- Always check image count before including Twitter in carousel posts
- Twitter video posts may fail for large files (known Blotato limitation)
- Instagram requires 1080x1920 vertical video format
- LinkedIn supports up to 3000 characters
- Twitter/X supports up to 280 characters (or 25,000 for long posts)

# Blotato Multi-Platform Posting

A Claude Code integration for posting content to multiple social media platforms using Blotato's API.

## Quick Setup

1. **Add your API key** to `config.json`:
   ```json
   {
     "api_key": "YOUR_ACTUAL_API_KEY",
     "base_url": "https://backend.blotato.com"
   }
   ```

2. **Get your API key** from Blotato:
   - Go to https://www.blotato.com/
   - Navigate to Settings → API Access
   - Copy your API key

## Usage

### Via Claude Code Commands

Use these slash commands to interact with Blotato:

**Post immediately:**
```
/blotato-post
```

**Schedule a post:**
```
/blotato-schedule
```

**Upload media:**
```
/blotato-upload
```

Claude will guide you through each step (content, platforms, timing, etc.).

**Media uploads now use Cloudinary MCP** for direct local file uploads - no need for public URLs.

### Via Command Line

#### Post to Platforms

```bash
cd .claude/skills/blotato-posting/scripts
./post.sh "Your content here" "twitter,linkedin,threads"
```

#### Schedule a Post

```bash
./post.sh "Scheduled content" "twitter,linkedin" "2025-10-29T09:00:00Z"
```

#### Upload Media First

**Cloudinary MCP method (preferred):**
```bash
# Use Claude Code with Cloudinary MCP to upload local files
# Automatically handles: local_file → Cloudinary → Blotato
```

**Manual method (public URLs):**
```bash
# Upload from public URL
./upload-media.sh "https://cloudinary.com/.../image.jpg"

# Returns Blotato-hosted media URL
```

Then post with media:
```bash
./post.sh "Check out this photo!" "instagram,twitter" "" "https://database.blotato.io/storage/.../image.jpeg"
```

## Supported Platforms

- **Twitter** - 280 char limit
- **LinkedIn** - Professional content (reconnect if account expires)
- **Instagram** - Requires media (images/videos)
- **Facebook**
- **TikTok** - Video-focused, vertical format
- **YouTube** - Requires title, privacyStatus, shouldNotifySubscribers
- **Threads** - 500 char limit (strictly enforced)
- **Bluesky** - Twitter-style content
- **Pinterest** - Requires images

### Important Platform Requirements

⚠️ **YouTube**: Must include `title`, `privacyStatus`, and `shouldNotifySubscribers` in post payload
⚠️ **Threads**: Content limited to 500 characters maximum
⚠️ **Instagram/Pinterest**: Requires media files

See SKILL.md for complete platform-specific requirements.

## Rate Limits

- **Publishing posts**: 30 requests per minute
- **Uploading media**: 10 requests per minute

## Files

- `config.json` - API configuration
- `scripts/post.sh` - CLI posting helper
- `scripts/upload-media.sh` - CLI media upload helper
- `README.md` - This file

## Commands

- `.claude/commands/blotato-post.md` - Immediate posting command
- `.claude/commands/blotato-schedule.md` - Scheduled posting command
- `.claude/commands/blotato-upload.md` - Media upload command

## Examples

### Simple Text Post
```bash
./scripts/post.sh "Hello from Claude Code!" "twitter,linkedin"
```

### Cross-Platform Announcement
```bash
./scripts/post.sh "🎉 Big news coming soon! Stay tuned..." "twitter,linkedin,threads,bluesky"
```

### Scheduled Post
```bash
./scripts/post.sh "Good morning! ☀️" "twitter" "2025-10-29T09:00:00Z"
```

## Notes

- API access requires a paid Blotato subscription
- Always use ISO 8601 format for scheduled times (e.g., `2025-10-29T09:00:00Z`)
- Media must be uploaded before including in posts
- `auto_optimize` is enabled by default for platform-specific formatting

## Documentation

- Blotato API Docs: https://help.blotato.com/api/start
- API Reference: https://help.blotato.com/api/api-reference

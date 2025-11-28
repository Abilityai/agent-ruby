---
description: Upload media to Cloudinary and get public URL
---

# Upload Media Command

Upload images, videos, or other media files to Cloudinary for use in social media posts.

## Usage

```
/upload-media <file path> [options]
```

## Parameters

- **file path**: Local file path or URL
  - `/Users/eugene/Desktop/image.png`
  - `ContentHub/Media/video.mp4`
  - `https://example.com/image.jpg` (will download first)

- **options** (optional):
  - `--type=<image|video|raw>` - Media type (auto-detected if omitted)
  - `--folder=<folder>` - Cloudinary folder name
  - `--public-id=<id>` - Custom public ID
  - `--overwrite` - Overwrite existing file

## Examples

### Upload Image
```
/upload-media /Users/eugene/Desktop/framework.png
```

### Upload Video to Specific Folder
```
/upload-media ContentHub/Media/ai-video.mp4 --folder=eugene-videos
```

### Upload with Custom ID
```
/upload-media image.png --public-id=ai-adoption-framework-2025-11
```

### Upload and Overwrite
```
/upload-media updated-image.png --public-id=framework --overwrite
```

## Workflow

1. **Validate File**
   - Check file exists (if local path)
   - Verify file size within limits
   - Detect media type if not specified

2. **Download if URL**
   - If file is URL, download to temp
   - Use temp file for upload

3. **Upload to Cloudinary**
   - Use cloudinary-asset-mgmt MCP
   - Apply specified options
   - Get upload response with URLs

4. **Return URL**
   - Display public URL
   - Show secure URL (https)
   - Provide thumbnail URL (for images)
   - Show Cloudinary dashboard link

5. **Optional: Save to Cache**
   - Copy to ContentHub/Media/ for local reference
   - Save metadata JSON with URLs

## Response Format

```
✅ Media uploaded successfully!

Public URL: https://res.cloudinary.com/dfs5yfioa/image/upload/v1699999999/filename.png

Secure URL: https://res.cloudinary.com/dfs5yfioa/image/upload/v1699999999/filename.png

Thumbnail (if image): https://res.cloudinary.com/dfs5yfioa/image/upload/c_thumb,w_200/filename.png

Cloudinary Dashboard: https://console.cloudinary.com/console/dfs5yfioa/media_library/asset/image/upload/filename

File Details:
- Type: image/png
- Size: 245 KB
- Format: PNG
- Dimensions: 1920x1080
- Public ID: filename
```

## File Size Limits

### Image
- Max: 10 MB (free tier)
- Recommended: < 5 MB for fast loading

### Video
- Max: 100 MB (free tier)
- Recommended: < 50 MB for social media

### Other (PDF, documents)
- Max: 10 MB
- Use `--type=raw` for non-image/video files

## Cloudinary Configuration

**Cloud Name**: dfs5yfioa

**Credentials**: Stored in `.claude/agents/.mcp.json`
```json
{
  "mcpServers": {
    "cloudinary-asset-mgmt": {
      "command": "npx",
      "args": [
        "-y",
        "--package",
        "@cloudinary/asset-management",
        "--",
        "mcp",
        "start",
        "--api-key",
        "476858566113846",
        "--api-secret",
        "7lfuVGx4HZZ0xC5v_WfvP5PtZqg",
        "--cloud-name",
        "dfs5yfioa"
      ]
    }
  }
}
```

## Use Cases

### 1. Prepare Media for Social Posts
```
/upload-media screenshot.png
# Get URL → Use in /post-now or /schedule-post
```

### 2. Upload Video for Multi-Platform Posting
```
/upload-media ai-video.mp4 --folder=social-media
# Get URL → Post to Instagram, TikTok, LinkedIn
```

### 3. Create Carousel (Multiple Images)
```
/upload-media image1.png --folder=carousel-ai-adoption
/upload-media image2.png --folder=carousel-ai-adoption
/upload-media image3.png --folder=carousel-ai-adoption
# Get URLs → Use in Instagram carousel post
```

### 4. Upload GIF from Giphy
```
# First use giphy-manager sub-agent to get GIF URL
# Then:
/upload-media https://media.giphy.com/media/xxx/giphy.gif
# Uploads to Cloudinary for permanent hosting
```

### 5. Backup Important Media
```
/upload-media important-video.mp4 --folder=backup --public-id=backup-2025-11-14
# Permanent cloud storage with custom ID
```

## Advanced Options

### Image Transformations
After upload, can generate transformed URLs:

- **Resize**: `.../c_scale,w_800/image.png`
- **Crop**: `.../c_fill,w_1080,h_1920/image.png`
- **Quality**: `.../q_auto/image.png`
- **Format**: `.../f_auto/image.png`

### Video Transformations
- **Quality**: `.../q_auto/video.mp4`
- **Format**: `.../f_auto/video.mp4`
- **Preview**: `.../so_0,eo_3/video.mp4` (first 3 seconds)

### Folder Organization
Suggested folder structure in Cloudinary:
- `social-media/` - Posts and content
- `eugene-videos/` - HeyGen and produced videos
- `frameworks/` - Framework images
- `backup/` - Important media backup
- `temp/` - Temporary uploads (manual cleanup)

## Metadata Storage (Optional)

Save upload metadata to ContentHub/Media/:

```json
{
  "filename": "ai-adoption-framework.png",
  "cloudinary_url": "https://res.cloudinary.com/...",
  "public_id": "ai-adoption-framework",
  "uploaded_at": "2025-11-14T14:30:00Z",
  "type": "image",
  "size_bytes": 245760,
  "dimensions": "1920x1080",
  "folder": "frameworks",
  "usage": [
    {
      "platform": "linkedin",
      "post_url": "https://linkedin.com/posts/...",
      "posted_at": "2025-11-14T15:00:00Z"
    }
  ]
}
```

## Error Handling

### File Not Found
- Verify path is correct
- Check file permissions
- Try absolute path

### Upload Fails
- Check internet connection
- Verify Cloudinary credentials in .mcp.json
- Check file size limits
- Try again (transient network issues)

### Quota Exceeded
- Check Cloudinary dashboard for quota
- Delete old/unused files
- Consider upgrading plan

## Cloudinary Dashboard

Access: https://console.cloudinary.com/console/dfs5yfioa/

Features:
- View all uploaded files
- Organize into folders
- Apply transformations
- Monitor usage and quota
- Delete old files
- Generate transformed URLs

## Integration with Other Commands

```
# Upload → Post workflow
/upload-media screenshot.png
# → Get URL → Copy URL
/post-now linkedin image "Check out this framework!" <URL>

# Upload → Video workflow
/upload-media video.mp4
# → Get URL → Use in /create-video as source

# Upload → Schedule workflow
/upload-media image.png
# → Get URL
/schedule-post "tomorrow 9am" linkedin image "Post text" <URL>
```

## Tips

- **Organize**: Use folders for different content types
- **Name clearly**: Use descriptive public IDs
- **Clean up**: Delete unused media monthly
- **Monitor quota**: Check usage in Cloudinary dashboard
- **Backup important**: Use --public-id for critical media
- **Test first**: Upload to temp folder for testing

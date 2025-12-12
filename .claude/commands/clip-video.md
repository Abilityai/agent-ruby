# Clip Video with Klap API

Generate viral shorts from a long-form video using Klap AI.

## Instructions

You are tasked with clipping a video into viral shorts using the Klap API.

**Requirements:**
1. User will provide a video file path (local MP4)
2. You must upload it to Cloudinary first to get a public URL
3. Submit to Klap API for shorts generation
4. Wait for processing to complete
5. Download all generated shorts to **TWO locations**:
   - The same directory as the source video
   - Central shorts folder: `$CONTENT_DIR/CutShorts`
6. Save metadata (virality scores, captions) to both directories

**Klap API Details:**
- API Key: Set via `KLAP_API_KEY` environment variable
- Base URL: `https://api.klap.app/v2`
- Python script available: `./scripts/klap_clipper.py`

**Workflow:**

1. **Upload to Cloudinary:**
   - Use `mcp__cloudinary-asset-mgmt__upload-asset` tool
   - Resource type: `video`
   - Get the `secure_url` from response

2. **Submit to Klap:**
   ```bash
   curl -X POST 'https://api.klap.app/v2/tasks/video-to-shorts' \
     -H "Authorization: Bearer $KLAP_API_KEY" \
     -H 'Content-Type: application/json' \
     -d '{
       "source_video_url": "<cloudinary_url>",
       "language": "en",
       "max_duration": 60,
       "target_clip_count": 5,
       "editing_options": {
         "captions": true,
         "reframe": true,
         "emojis": false,
         "intro_title": false
       }
     }'
   ```

3. **Poll for completion:**
   - GET `/v2/tasks/{task_id}` every 30 seconds
   - Wait until `status` = `"ready"`

4. **Get shorts:**
   - GET `/v2/projects/{output_id}`
   - Returns array of shorts with virality scores

5. **Export and download each short:**
   - POST `/v2/projects/{folder_id}/{project_id}/exports`
   - Poll GET `/v2/projects/{folder_id}/{project_id}/exports/{export_id}`
   - Download from `src_url` when ready

6. **Save to TWO locations:**
   - Download each short to the same folder as source video
   - Copy each short to `$CONTENT_DIR/CutShorts`
   - Name format: `short_01_score_68.mp4`, `short_02_score_72.mp4`, etc.
   - Save metadata JSON: `klap_results.json` in both locations
   - Create a subfolder in CutShorts named after the source video (without extension) to organize clips

**Output Structure:**
```
# Location 1: Original video folder
/path/to/video/folder/
├── original_video.mp4
├── transcript.md
├── short_01_score_68.mp4          # Sorted by virality score (highest first)
├── short_02_score_65.mp4
├── short_03_score_62.mp4
├── klap_results.json              # Full metadata with captions, scores, etc.

# Location 2: Central CutShorts folder
$HOME/.../[User] Personal Brand/CutShorts/
└── original_video_name/
    ├── short_01_score_68.mp4
    ├── short_02_score_65.mp4
    ├── short_03_score_62.mp4
    └── klap_results.json
```

**Important:**
- Sort shorts by virality score (descending) when naming files
- Include virality score in filename for easy identification
- Save platform-specific captions in klap_results.json
- **Create subfolder in CutShorts** named after source video (e.g., "AI_Agents_adoption_bottlenecks_2" from "AI Agents adoption bottlenecks - 2.mp4")
- Ensure both locations have identical files (shorts + metadata)
- Report total processing time, cost estimate, and both save locations to user

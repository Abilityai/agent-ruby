---
name: Generate Image
description: Generate images using Replicate's google/imagen-4-ultra model
---

# Generate Image Command

Generate high-quality images using Google's Imagen 4 Ultra model via Replicate MCP.

## **Model Information**

**Model:** `google/imagen-4-ultra`
**Provider:** Replicate
**Type:** Text-to-image generation
**Quality:** Ultra-high quality, photorealistic outputs

## Task

When the user invokes this command, use the Replicate MCP server to generate images using the google/imagen-4-ultra model.

## Command Usage

**With project folder:**
```
/generate-image <description> for <project_folder_path>
/generate-image <description> in <project_folder_path>
```
→ Saves to: `<project_folder_path>/thumbnails/`

**Without project folder:**
```
/generate-image <description>
```
→ Saves to: `$VAULT_BASE_PATH/generated_images/`

**Examples:**
```bash
# With project folder
/generate-image Create 3 YouTube thumbnails for $HOME/Projects/MyVideo/

# Without project folder (uses generated_images/)
/generate-image Create an Instagram post with motivational quote
```

## Workflow

### 1. **Get Model Information (First Time or If Needed)**

```
Use: mcp__replicate__search
Query: "google imagen-4-ultra"
jq_filter: ".models[].model.name"
```

Or get specific model details:
```
Use: mcp__replicate__get_models
model_owner: "google"
model_name: "imagen-4-ultra"
jq_filter: ".latest_version.openapi_schema.components.schemas.Input"
```

### 2. **Create Prediction (Generate Image)**

```
Use: mcp__replicate__create_predictions
Parameters:
- version: "google/imagen-4-ultra:latest" (or specific version ID)
- input: {
    "prompt": "<user's image description>",
    "aspect_ratio": "16:9" | "9:16" | "1:1" | "4:3" | "3:4" (optional, default: "1:1"),
    "output_format": "png" | "jpg" | "webp" (optional, default: "jpg"),
    "output_quality": 80 (optional, 0-100, default: 80),
    "safety_tolerance": 1-6 (optional, higher = less filtering, default: 2),
    "negative_prompt": "<things to avoid>" (optional),
    "seed": <number> (optional, for reproducibility)
  }
- Prefer: "wait" (wait up to 60 seconds for result)
- jq_filter: ".output" (CRITICAL - only return the image URL)
```

### 3. **Check Prediction Status (If Async)**

If prediction returns with status "starting" or "processing":
```
Use: mcp__replicate__get_predictions
prediction_id: "<prediction_id_from_create>"
jq_filter: ".status, .output"
```

Poll every 5-10 seconds until status is "succeeded" or "failed".

### 4. **Save Images Locally (IMPORTANT)**

**Always save generated images locally after creation** because Replicate URLs expire in 24 hours.

**Determine save location:**
- **If project folder provided**: Save to `<project_folder>/thumbnails/`
- **If no project folder**: Save to `$VAULT_BASE_PATH/generated_images/`

**Workflow:**
```bash
# 1. Determine save directory
if [[ -n "$PROJECT_FOLDER" ]]; then
  SAVE_DIR="$PROJECT_FOLDER/thumbnails"
else
  SAVE_DIR="$VAULT_BASE_PATH/generated_images"
fi

# 2. Create directory if needed
mkdir -p "$SAVE_DIR"

# 3. Download image with descriptive filename
cd "$SAVE_DIR"
curl -o "thumbnail_v1_description.png" "<replicate_url>"
```

**Filename Convention:**
- Format: `thumbnail_v{number}_{description}.{ext}`
- Examples:
  - `thumbnail_v1_gradient_coral_gray.png`
  - `thumbnail_v2_tech_dark_navy.png`
  - `thumbnail_v3_minimal_white.png`
  - `image_v1_product_photo.jpg`

## Common Parameters

### **Aspect Ratios for Different Use Cases:**
- **YouTube Thumbnails**: "16:9" (1920x1080)
- **Instagram Posts**: "1:1" (1080x1080)
- **Instagram Stories**: "9:16" (1080x1920)
- **LinkedIn Posts**: "4:3" or "16:9"
- **Twitter/X Posts**: "16:9" or "1:1"
- **Blog Headers**: "16:9" or "3:1"

### **Output Format:**
- **PNG**: Best for graphics with text, transparency needs
- **JPG**: Best for photos, smaller file size
- **WEBP**: Best for web, smallest file size

### **Safety Tolerance:**
- **1-2**: Strict filtering (default)
- **3-4**: Moderate filtering
- **5-6**: Minimal filtering (use carefully)

## Examples

### Example 1: YouTube Thumbnail (With Project Folder)
```
User: "Generate a YouTube thumbnail for my video project at
      $HOME/Projects/MyVideo/ with large text 'ONE TRANSCRIPT'
      on top and '50 POSTS' below"

Claude executes:
1. Create prediction:
   mcp__replicate__create_predictions(
     version: "google/imagen-4-ultra",
     input: {
       "prompt": "Professional YouTube thumbnail with very large bold text 'ONE TRANSCRIPT'
                  at the top in dark gray and '50 POSTS' at the bottom in bright red.
                  Gradient background from soft pale red to light gray. Semi-transparent
                  white card behind text. High contrast, clean modern design,
                  readable at small size. Professional tech aesthetic.",
       "aspect_ratio": "16:9",
       "output_format": "png",
       "output_quality": 95
     },
     Prefer: "wait",
     jq_filter: ".output"
   )

2. Save locally:
   mkdir -p "$HOME/Projects/MyVideo/thumbnails"
   cd "$HOME/Projects/MyVideo/thumbnails"
   curl -o "thumbnail_v1_one_transcript_50_posts.png" "<replicate_url>"
```

### Example 2: Instagram Post
```
User: "Create an inspirational quote image for Instagram with the text
      'Build systems, not goals'"

Claude executes:
mcp__replicate__create_predictions(
  version: "google/imagen-4-ultra",
  input: {
    "prompt": "Clean minimalist Instagram post design with elegant typography.
               Text reads 'Build systems, not goals'. Soft pastel background,
               modern sans-serif font, centered composition, professional branding aesthetic.",
    "aspect_ratio": "1:1",
    "output_format": "jpg",
    "output_quality": 90
  },
  Prefer: "wait",
  jq_filter: ".output"
)
```

### Example 3: Product Photo
```
User: "Generate a product photo of a sleek AI robot assistant on a desk"

Claude executes:
mcp__replicate__create_predictions(
  version: "google/imagen-4-ultra",
  input: {
    "prompt": "Photorealistic product photography of a sleek white AI robot assistant
               on a modern minimalist desk. Soft natural lighting from window.
               Clean white background. Professional studio quality. 8K resolution.",
    "aspect_ratio": "4:3",
    "output_format": "jpg",
    "output_quality": 95,
    "negative_prompt": "cartoon, illustration, low quality, blurry, distorted"
  },
  Prefer: "wait",
  jq_filter: ".output"
)
```

### Example 4: Batch Generation (Multiple Variations)
```
User: "Generate 3 variations of a sunset beach scene"

Claude executes:
1. Create 3 predictions with different seeds:
   - Variation 1: seed: 1234 → URL1
   - Variation 2: seed: 5678 → URL2
   - Variation 3: seed: 9012 → URL3

2. Save all to generated_images folder:
   mkdir -p "$VAULT_BASE_PATH/generated_images"
   cd "$VAULT_BASE_PATH/generated_images"

   curl -o "sunset_v1_seed1234.png" "<url1>"
   curl -o "sunset_v2_seed5678.png" "<url2>"
   curl -o "sunset_v3_seed9012.png" "<url3>"

3. Report: "Saved 3 variations to generated_images/"
```

## Best Practices

### ✅ DO:
- **Save images locally immediately** after generation (URLs expire in 24 hours)
- **Use jq_filter: ".output"** on ALL predictions (reduces response size by 95%)
- **Be specific in prompts**: Include lighting, style, mood, quality level
- **Specify aspect ratio** for the use case (YouTube, Instagram, etc.)
- **Use Prefer: "wait"** for synchronous generation (up to 60 seconds)
- **Include negative prompts** to avoid unwanted elements
- **Set output_quality: 90-95** for final production images
- **Save to project/thumbnails/** if project folder provided
- **Save to generated_images/** if no project folder

### ❌ DON'T:
- Forget the jq_filter (wastes tokens and context)
- Use vague prompts like "nice image"
- Skip aspect ratio specification
- Ignore output format for the platform
- Chain operations before prediction completes

## Prompt Engineering Tips

### **For Text in Images (Thumbnails, Quotes):**
```
"Very large bold text '[TEXT]' occupying 70% of frame,
[STYLE] font, [COLOR] on [BACKGROUND]. High contrast,
readable at thumbnail size. Professional design."
```

### **For Photorealistic Images:**
```
"Photorealistic [SUBJECT], professional photography,
natural lighting, 8K resolution, sharp focus,
detailed, [STYLE] aesthetic"
```

### **For Illustrations/Graphics:**
```
"Clean modern illustration of [SUBJECT], [COLOR PALETTE],
minimalist design, vector style, professional branding,
[MOOD/TONE]"
```

### **For Product Photos:**
```
"Professional product photography of [PRODUCT],
studio lighting, white background, 4K quality,
commercial photography, clean and sharp"
```

## Integration with Other Workflows

### **After Image Generation:**

**For Social Media Posting:**
1. Image generated → Get Replicate URL
2. Upload to Cloudinary (for permanent storage):
   ```
   mcp__cloudinary-mcp-server__upload(source="<replicate_url>", resourceType="image")
   ```
3. Use with `/blotato-post` or `/blotato-schedule`

**For Carousel Creation:**
1. Generate multiple images (3-5)
2. Upload each to Cloudinary
3. Use in LinkedIn carousel or Instagram carousel posts

**For Thumbnail Testing:**
1. Generate 3-5 variations with different styles
2. Save all URLs
3. A/B test which performs best

## Error Handling

### Common Errors:

**"Model not found"**
- Solution: Search for the correct model name using `mcp__replicate__search`

**"Prediction failed"**
- Check prompt doesn't violate content policies
- Reduce safety_tolerance if too strict
- Try different negative_prompt

**"Timeout"**
- Remove `Prefer: "wait"` to get async prediction
- Poll with `get_predictions` until complete

**"Invalid aspect_ratio"**
- Valid options: "1:1", "16:9", "9:16", "4:3", "3:4"
- Check spelling and format

**"Output too large"**
- Reduce output_quality to 80-85
- Use "webp" format for smaller files

## Rate Limits

- **Replicate API**: Based on your account tier
- **Prediction polling**: Wait 5-10 seconds between status checks
- **Batch generation**: Spread requests over time to avoid rate limits

## Cost Considerations

- **Imagen 4 Ultra**: Premium model, higher cost per generation
- **Approximate cost**: $0.02-0.05 per image (check Replicate pricing)
- **Optimization**: Use lower output_quality for drafts, high for finals

## Output Format & Local Storage

### **Replicate URLs (Temporary)**
The command returns a Replicate URL to the generated image:
```
https://replicate.delivery/pbxt/[hash]/output.png
```

**⚠️ CRITICAL:** Replicate URLs expire after 24 hours!

### **Local Storage (Required)**

**ALWAYS save images locally immediately after generation.**

**Save Location Logic:**
```bash
# If user provides project folder path
if [[ "$USER_MESSAGE" == *"/Users/"* ]] || [[ "$USER_MESSAGE" == *"project"* ]]; then
  # Extract project folder from context
  # Save to: <project_folder>/thumbnails/
  SAVE_DIR="<extracted_project_folder>/thumbnails"
else
  # No project folder mentioned
  # Save to: $VAULT_BASE_PATH/generated_images/
  SAVE_DIR="$VAULT_BASE_PATH/generated_images"
fi

mkdir -p "$SAVE_DIR"
cd "$SAVE_DIR"
curl -o "descriptive_filename.png" "<replicate_url>"
```

**Examples:**
```bash
# With project folder:
$HOME/Library/CloudStorage/.../MyProject/thumbnails/thumbnail_v1.png

# Without project folder:
$CORNELIUS_DIR/generated_images/thumbnail_v1.png
```

## Helper Commands

### Check prediction status:
```bash
# Get prediction details
mcp__replicate__get_predictions(prediction_id: "abc123", jq_filter: ".status, .output")
```

### List recent predictions:
```bash
mcp__replicate__list_predictions(jq_filter: ".results[].id, .results[].status")
```

### Search for alternative models:
```bash
mcp__replicate__search(query: "text to image", jq_filter: ".models[].model.name")
```

## Advanced Usage

### **Reproducible Generation:**
Use same seed for consistent results:
```
seed: 42 (any number)
```

### **Negative Prompts:**
Exclude unwanted elements:
```
negative_prompt: "blurry, low quality, distorted, text, watermark, cartoon, 3D render"
```

### **Style Modifiers:**
Add to prompt:
- "professional photography"
- "studio lighting"
- "8K resolution"
- "cinematic composition"
- "minimalist design"
- "vibrant colors"
- "soft natural lighting"

## Complete Example Workflow

```
User: "I need 3 YouTube thumbnail variations for my AI content video
      in $HOME/Projects/AIVideo/"

Claude:
1. Generates Variation 1:
   - Prompt: "Bold text 'AI CONTENT REVOLUTION' with robot icon,
             tech background, 16:9, high contrast"
   - aspect_ratio: "16:9", seed: 1111
   - Returns: URL1

2. Generates Variation 2:
   - Same prompt with different color scheme
   - seed: 2222
   - Returns: URL2

3. Generates Variation 3:
   - Same prompt with different layout
   - seed: 3333
   - Returns: URL3

4. Saves all locally:
   mkdir -p "$HOME/Projects/AIVideo/thumbnails"
   cd "$HOME/Projects/AIVideo/thumbnails"

   curl -o "thumbnail_v1_ai_revolution_robot.png" "<URL1>"
   curl -o "thumbnail_v2_ai_revolution_colors.png" "<URL2>"
   curl -o "thumbnail_v3_ai_revolution_layout.png" "<URL3>"

5. Reports:
   "✅ Generated 3 thumbnail variations!

   Saved to: $HOME/Projects/AIVideo/thumbnails/
   - thumbnail_v1_ai_revolution_robot.png (802KB)
   - thumbnail_v2_ai_revolution_colors.png (934KB)
   - thumbnail_v3_ai_revolution_layout.png (508KB)

   Would you like me to upload these to Cloudinary for social media posting?"
```

---

**Remember:** Always use `jq_filter: ".output"` to keep responses minimal and fast! 🚀

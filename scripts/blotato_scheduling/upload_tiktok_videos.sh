#!/bin/bash

CLOUD_NAME="${CLOUDINARY_CLOUD_NAME:-dfs5yfioa}"
API_KEY="${CLOUDINARY_API_KEY:?Error: CLOUDINARY_API_KEY not set}"

# Videos to upload for TikTok
declare -a VIDEOS=(
    "$CONTENT_DIR/ClipShorts/Data-Privacy_FINAL/short_01_score_90.mp4"
    "$CONTENT_DIR/ClipShorts/video_no_subs_1/short_02_score_86.mp4"
    "$CONTENT_DIR/ClipShorts/short/short_01_score_82.mp4"
    "$CONTENT_DIR/ClipShorts/Data-Privacy_FINAL/short_02_score_82.mp4"
    "$CONTENT_DIR/ClipShorts/video_no_subs_1/short_03_score_78.mp4"
    "$CONTENT_DIR/ClipShorts/video_no_subs_1/short_04_score_78.mp4"
    "$CONTENT_DIR/ClipShorts/Data-Privacy_FINAL/short_04_score_78.mp4"
    "$CONTENT_DIR/ClipShorts/Data-Privacy_FINAL/short_05_score_78.mp4"
    "$CONTENT_DIR/ClipShorts/short/short_05_score_72.mp4"
)

echo "Uploading ${#VIDEOS[@]} videos to Cloudinary..."
echo "============================================================"
echo ""

> cloudinary_urls.json
echo "[" >> cloudinary_urls.json

for i in "${!VIDEOS[@]}"; do
    VIDEO="${VIDEOS[$i]}"
    FILENAME=$(basename "$VIDEO")

    echo "[$((i+1))/${#VIDEOS[@]}] Uploading: $FILENAME"

    RESPONSE=$(curl -s -X POST "https://api.cloudinary.com/v1_1/${CLOUD_NAME}/video/upload" \
        -F "file=@${VIDEO}" \
        -F "folder=klap_shorts" \
        -F "api_key=${API_KEY}" \
        -F "upload_preset=ml_default" 2>&1)

    URL=$(echo "$RESPONSE" | jq -r '.secure_url // empty')

    if [ -n "$URL" ]; then
        echo "  ✅ $URL"
        echo "  {\"filename\": \"$FILENAME\", \"url\": \"$URL\"}," >> cloudinary_urls.json
    else
        echo "  ❌ Failed: $RESPONSE"
    fi
    echo ""
done

echo "]" >> cloudinary_urls.json
echo "✓ Upload complete! URLs saved to cloudinary_urls.json"

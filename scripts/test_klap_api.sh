#!/bin/bash

# Klap API Test Script
# Loads credentials from .env file

# Load environment variables from .env
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/../.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

API_KEY="${KLAP_API_KEY}"
BASE_URL="${KLAP_BASE_URL}"

if [ -z "$API_KEY" ]; then
    echo "Error: KLAP_API_KEY not set in .env"
    exit 1
fi

# Test video URL (public example - replace with your video URL)
VIDEO_URL="$1"

if [ -z "$VIDEO_URL" ]; then
    echo "Usage: $0 <video_url>"
    echo "Example: $0 https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    exit 1
fi

echo "=== Klap API Test ==="
echo "Video URL: $VIDEO_URL"
echo ""

# Step 1: Submit video for processing
echo "Step 1: Submitting video to Klap..."
TASK_RESPONSE=$(curl -s -X POST "$BASE_URL/tasks/video-to-shorts" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"source_video_url\": \"$VIDEO_URL\",
    \"language\": \"en\",
    \"max_duration\": 60,
    \"target_clip_count\": 5,
    \"editing_options\": {
      \"captions\": true,
      \"reframe\": true,
      \"intro_title\": false,
      \"emojis\": false
    }
  }")

echo "Response:"
echo "$TASK_RESPONSE" | jq '.'

# Extract task ID
TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')

if [ "$TASK_ID" == "null" ] || [ -z "$TASK_ID" ]; then
    echo ""
    echo "ERROR: Failed to create task. Check API key and video URL."
    echo "Full response: $TASK_RESPONSE"
    exit 1
fi

echo ""
echo "Task ID: $TASK_ID"
echo "Status: Processing started..."
echo ""

# Step 2: Poll for completion
echo "Step 2: Polling task status (checking every 30 seconds)..."
STATUS="processing"
POLL_COUNT=0
MAX_POLLS=60  # 30 minutes max

while [ "$STATUS" == "processing" ] && [ $POLL_COUNT -lt $MAX_POLLS ]; do
    sleep 30
    POLL_COUNT=$((POLL_COUNT + 1))

    STATUS_RESPONSE=$(curl -s -X GET "$BASE_URL/tasks/$TASK_ID" \
      -H "Authorization: Bearer $API_KEY")

    STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.status')

    echo "[$POLL_COUNT] Status: $STATUS"

    if [ "$STATUS" == "error" ]; then
        echo ""
        echo "ERROR: Task failed"
        echo "$STATUS_RESPONSE" | jq '.'
        exit 1
    fi
done

if [ "$STATUS" != "ready" ]; then
    echo ""
    echo "TIMEOUT: Task still processing after 30 minutes"
    exit 1
fi

echo ""
echo "✓ Task completed successfully!"
echo ""

# Step 3: Get output folder ID
OUTPUT_ID=$(echo "$STATUS_RESPONSE" | jq -r '.output_id')
echo "Output Folder ID: $OUTPUT_ID"
echo ""

# Step 4: Retrieve generated shorts
echo "Step 3: Retrieving generated shorts..."
PROJECTS_RESPONSE=$(curl -s -X GET "$BASE_URL/projects/$OUTPUT_ID" \
  -H "Authorization: Bearer $API_KEY")

echo "Generated Shorts:"
echo "$PROJECTS_RESPONSE" | jq '.[] | {id: .id, virality_score: .virality_score, duration: .duration}'

echo ""
echo "=== Summary ==="
echo "Total shorts generated: $(echo "$PROJECTS_RESPONSE" | jq '. | length')"
echo ""
echo "Top 3 by virality score:"
echo "$PROJECTS_RESPONSE" | jq -r 'sort_by(-.virality_score) | .[:3] | .[] | "\(.virality_score) - \(.id)"'
echo ""
echo "To export a short, use:"
echo "curl -X POST \"$BASE_URL/projects/$OUTPUT_ID/{project_id}/exports\" \\"
echo "  -H \"Authorization: Bearer $API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{}'"

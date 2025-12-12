#!/bin/bash

# Blotato Media Upload Helper Script
# Usage: ./upload-media.sh "https://url-to-your-image-or-video.jpg"
#
# IMPORTANT: Blotato requires a publicly accessible URL (NOT a local file path)
# - Dropbox: Change dl=0 to dl=1 at the end
# - Google Drive: Use https://drive.google.com/uc?export=download&id=FILE_ID
# - Imgur: Use direct image links (https://i.imgur.com/xxx.jpg)

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../config.json"
ENV_FILE="${SCRIPT_DIR}/../../../../.env"

# Load environment variables from .env
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Load credentials from environment
API_KEY="${BLOTATO_API_KEY}"
BASE_URL="${BLOTATO_BASE_URL}"

# Validate API key
if [ -z "$API_KEY" ]; then
    echo "Error: BLOTATO_API_KEY not set in .env"
    exit 1
fi

# Parse arguments
MEDIA_URL="$1"

if [ -z "$MEDIA_URL" ]; then
    echo "Usage: $0 \"https://url-to-your-media.jpg\""
    echo ""
    echo "IMPORTANT: Provide a publicly accessible URL (NOT a local file path)"
    echo ""
    echo "Supported sources:"
    echo "  - Dropbox: Change dl=0 to dl=1"
    echo "  - Google Drive: https://drive.google.com/uc?export=download&id=FILE_ID"
    echo "  - Imgur: https://i.imgur.com/xxx.jpg"
    echo "  - Any public URL"
    exit 1
fi

# Validate URL format
if [[ ! "$MEDIA_URL" =~ ^https?:// ]]; then
    echo "Error: Invalid URL format. Must start with http:// or https://"
    echo "Provided: $MEDIA_URL"
    exit 1
fi

# Upload media by sending URL to Blotato
echo "Uploading media from URL: $MEDIA_URL"
echo ""

RESPONSE=$(curl -s -X POST "${BASE_URL}/v2/media" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"${MEDIA_URL}\"}")

# Check response
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "Error: $(echo "$RESPONSE" | jq -r '.error')"
    echo ""
    echo "Full response:"
    echo "$RESPONSE" | jq .
    exit 1
else
    echo "Success!"
    BLOTATO_URL=$(echo "$RESPONSE" | jq -r '.url')
    echo "Blotato Media URL: $BLOTATO_URL"
    echo ""
    echo "Use this URL in your posts:"
    echo "$BLOTATO_URL"
fi

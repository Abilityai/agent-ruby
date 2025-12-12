#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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

API_KEY="${BLOTATO_API_KEY}"
BASE_URL="${BLOTATO_BASE_URL}"

IMAGE_FILE="$CORNELIUS_DIR/Brain/04-Output/Draft Posts/Cursor 2.0 Release/Google Imagen 4 Ultra Prediction (4).jpg"

echo "Uploading image..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/v2/media" \
    -H "Authorization: Bearer ${API_KEY}" \
    -F "file=@${IMAGE_FILE}" \
    -F "type=image")

echo "Full Response:"
echo "$RESPONSE" | jq .

echo ""
echo "Media URL:"
echo "$RESPONSE" | jq -r '.url // .mediaUrl // .data.url // .data.mediaUrl // "NOT_FOUND"'

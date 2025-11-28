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

IMAGE_FILE="/Users/eugene/Dropbox/Cornelius/Brain/04-Output/Draft Posts/Cursor 2.0 Release/Google Imagen 4 Ultra Prediction (4).jpg"

echo "Testing different upload methods..."
echo ""

# Method 1: Try with just the form data (no explicit content-type)
echo "Method 1: Standard multipart form upload"
RESPONSE1=$(curl -s -X POST "${BASE_URL}/v2/media" \
    -H "Authorization: Bearer ${API_KEY}" \
    -F "file=@${IMAGE_FILE}")
echo "$RESPONSE1" | jq .
echo ""

# Method 2: Try base64 encoding
echo "Method 2: Base64 encoded in JSON"
BASE64_IMAGE=$(base64 < "${IMAGE_FILE}")
RESPONSE2=$(curl -s -X POST "${BASE_URL}/v2/media" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"file\": \"${BASE64_IMAGE:0:100}...\", \"type\": \"image\"}")
echo "$RESPONSE2" | jq .
echo ""

# Method 3: Try with Content-Type application/octet-stream
echo "Method 3: Binary upload"
RESPONSE3=$(curl -s -X POST "${BASE_URL}/v2/media" \
    -H "Authorization: Bearer ${API_KEY}" \
    -H "Content-Type: application/octet-stream" \
    --data-binary "@${IMAGE_FILE}")
echo "$RESPONSE3" | jq .


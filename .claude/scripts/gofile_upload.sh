#!/bin/bash

# GoFile Upload Helper Script
# Uploads a file to GoFile and returns the shareable URL

set -e

# Load environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
else
    echo "Error: .env file not found at $PROJECT_ROOT/.env"
    echo "Please copy .env.example to .env and fill in your credentials"
    exit 1
fi

# GoFile credentials from environment
ACCOUNT_ID="${GOFILE_ACCOUNT_ID}"
API_TOKEN="${GOFILE_API_TOKEN}"
ROOT_FOLDER="${GOFILE_ROOT_FOLDER}"

# Validate credentials are set
if [ -z "$API_TOKEN" ] || [ -z "$ROOT_FOLDER" ]; then
    echo "Error: GoFile credentials not set in .env file"
    echo "Required: GOFILE_API_TOKEN, GOFILE_ROOT_FOLDER"
    exit 1
fi

# Check if file path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <file_path>"
    echo "Example: $0 /path/to/video.mp4"
    exit 1
fi

FILE_PATH="$1"

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

echo "Uploading file: $FILE_PATH"
echo "File size: $(du -h "$FILE_PATH" | cut -f1)"

# Step 1: Get upload server
echo "Getting upload server..."
SERVER=$(curl -s "https://api.gofile.io/servers" | jq -r '.data.servers[0].name')

if [ -z "$SERVER" ] || [ "$SERVER" == "null" ]; then
    echo "Error: Failed to get upload server"
    exit 1
fi

echo "Using server: $SERVER"

# Step 2: Upload file
echo "Uploading to GoFile..."
RESPONSE=$(curl -s -X POST "https://$SERVER.gofile.io/contents/uploadfile" \
  -H "Authorization: Bearer $API_TOKEN" \
  -F "file=@$FILE_PATH" \
  -F "folderId=$ROOT_FOLDER")

# Check if upload was successful
STATUS=$(echo "$RESPONSE" | jq -r '.status')

if [ "$STATUS" != "ok" ]; then
    echo "Error: Upload failed"
    echo "Response: $RESPONSE"
    exit 1
fi

# Extract download page URL
DOWNLOAD_URL=$(echo "$RESPONSE" | jq -r '.data.downloadPage')
FILE_ID=$(echo "$RESPONSE" | jq -r '.data.id')
FILE_SIZE=$(echo "$RESPONSE" | jq -r '.data.size')

echo ""
echo "✅ Upload successful!"
echo "Download URL: $DOWNLOAD_URL"
echo "File ID: $FILE_ID"
echo "Size: $FILE_SIZE bytes"
echo ""
echo "Use this URL with Blotato for posting to social media."
echo "File will auto-delete in 10-30 days."

# Return URL for script usage
echo "$DOWNLOAD_URL"

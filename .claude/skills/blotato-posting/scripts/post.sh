#!/bin/bash

# Blotato Posting Helper Script
# Usage: ./post.sh "content" "platform1,platform2,..." [schedule_time] [media_url1,media_url2,...]
#
# PLATFORM-SPECIFIC REQUIREMENTS:
# - YouTube: Requires title, privacyStatus, shouldNotifySubscribers (auto-handled)
# - Threads: 500 character limit maximum (must condense content)
# - Instagram/Pinterest: Requires media URLs
# - LinkedIn: Account may expire, reconnect in Blotato dashboard if needed
#
# CHARACTER LIMITS:
# - Twitter: 280 chars
# - Threads: 500 chars (strictly enforced)
# - Instagram: 2,200 chars

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

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: config.json not found at $CONFIG_FILE"
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
CONTENT="$1"
PLATFORMS="$2"
SCHEDULE_TIME="${3:-}"
MEDIA_URLS="${4:-}"

if [ -z "$CONTENT" ] || [ -z "$PLATFORMS" ]; then
    echo "Usage: $0 \"content\" \"platform1,platform2,...\" [schedule_time] [media_url1,media_url2,...]"
    echo ""
    echo "Platforms: twitter, linkedin, instagram, facebook, tiktok, youtube, threads, bluesky, pinterest"
    echo "Schedule time (optional): ISO 8601 format, e.g., 2025-10-29T09:00:00Z"
    echo "Media URLs (optional): Comma-separated list of media URLs"
    exit 1
fi

# Convert comma-separated platforms to array
IFS=',' read -ra PLATFORM_ARRAY <<< "$PLATFORMS"

# Convert comma-separated media URLs to JSON array
if [ -n "$MEDIA_URLS" ]; then
    IFS=',' read -ra MEDIA_ARRAY <<< "$MEDIA_URLS"
    MEDIA_JSON=$(printf '%s\n' "${MEDIA_ARRAY[@]}" | jq -R . | jq -s .)
else
    MEDIA_JSON="[]"
fi

# Function to get account ID for a platform
get_account_id() {
    local platform=$1
    jq -r ".account_ids.${platform} // empty" "$CONFIG_FILE"
}

# Post to each platform separately (since each needs its own accountId)
for platform in "${PLATFORM_ARRAY[@]}"; do
    # Trim whitespace
    platform=$(echo "$platform" | xargs)

    # Get account ID for this platform
    ACCOUNT_ID=$(get_account_id "$platform")

    if [ -z "$ACCOUNT_ID" ]; then
        echo "Warning: No account ID found for platform '$platform' - skipping"
        continue
    fi

    # Build post payload according to Blotato API structure
    # Extract title from content (first line)
    VIDEO_TITLE=$(echo "$CONTENT" | head -n 1)

    if [ -n "$SCHEDULE_TIME" ]; then
        if [ "$platform" == "youtube" ]; then
            # YouTube requires specific fields
            JSON_PAYLOAD=$(jq -n \
                --arg account_id "$ACCOUNT_ID" \
                --arg content "$CONTENT" \
                --arg platform "$platform" \
                --argjson media_urls "$MEDIA_JSON" \
                --arg scheduled_time "$SCHEDULE_TIME" \
                --arg title "$VIDEO_TITLE" \
                '{
                    post: {
                        accountId: $account_id,
                        content: {
                            text: $content,
                            mediaUrls: $media_urls,
                            platform: $platform
                        },
                        target: {
                            targetType: $platform,
                            title: $title,
                            privacyStatus: "public",
                            shouldNotifySubscribers: false
                        }
                    },
                    scheduledTime: $scheduled_time
                }')
        elif [ "$platform" == "tiktok" ]; then
            # TikTok requires specific fields
            JSON_PAYLOAD=$(jq -n \
                --arg account_id "$ACCOUNT_ID" \
                --arg content "$CONTENT" \
                --arg platform "$platform" \
                --argjson media_urls "$MEDIA_JSON" \
                --arg scheduled_time "$SCHEDULE_TIME" \
                '{
                    post: {
                        accountId: $account_id,
                        content: {
                            text: $content,
                            mediaUrls: $media_urls,
                            platform: $platform
                        },
                        target: {
                            targetType: $platform,
                            privacyLevel: "PUBLIC_TO_EVERYONE",
                            disabledComments: false,
                            disabledDuet: false,
                            disabledStitch: false,
                            isBrandedContent: false,
                            isYourBrand: false,
                            isAiGenerated: true
                        }
                    },
                    scheduledTime: $scheduled_time
                }')
        else
            JSON_PAYLOAD=$(jq -n \
                --arg account_id "$ACCOUNT_ID" \
                --arg content "$CONTENT" \
                --arg platform "$platform" \
                --argjson media_urls "$MEDIA_JSON" \
                --arg scheduled_time "$SCHEDULE_TIME" \
                '{
                    post: {
                        accountId: $account_id,
                        content: {
                            text: $content,
                            mediaUrls: $media_urls,
                            platform: $platform
                        },
                        target: {
                            targetType: $platform
                        }
                    },
                    scheduledTime: $scheduled_time
                }')
        fi
    else
        if [ "$platform" == "youtube" ]; then
            # YouTube requires specific fields
            JSON_PAYLOAD=$(jq -n \
                --arg account_id "$ACCOUNT_ID" \
                --arg content "$CONTENT" \
                --arg platform "$platform" \
                --argjson media_urls "$MEDIA_JSON" \
                --arg title "$VIDEO_TITLE" \
                '{
                    post: {
                        accountId: $account_id,
                        content: {
                            text: $content,
                            mediaUrls: $media_urls,
                            platform: $platform
                        },
                        target: {
                            targetType: $platform,
                            title: $title,
                            privacyStatus: "public",
                            shouldNotifySubscribers: false
                        }
                    }
                }')
        elif [ "$platform" == "tiktok" ]; then
            # TikTok requires specific fields
            JSON_PAYLOAD=$(jq -n \
                --arg account_id "$ACCOUNT_ID" \
                --arg content "$CONTENT" \
                --arg platform "$platform" \
                --argjson media_urls "$MEDIA_JSON" \
                '{
                    post: {
                        accountId: $account_id,
                        content: {
                            text: $content,
                            mediaUrls: $media_urls,
                            platform: $platform
                        },
                        target: {
                            targetType: $platform,
                            privacyLevel: "PUBLIC_TO_EVERYONE",
                            disabledComments: false,
                            disabledDuet: false,
                            disabledStitch: false,
                            isBrandedContent: false,
                            isYourBrand: false,
                            isAiGenerated: true
                        }
                    }
                }')
        else
            JSON_PAYLOAD=$(jq -n \
                --arg account_id "$ACCOUNT_ID" \
                --arg content "$CONTENT" \
                --arg platform "$platform" \
                --argjson media_urls "$MEDIA_JSON" \
                '{
                    post: {
                        accountId: $account_id,
                        content: {
                            text: $content,
                            mediaUrls: $media_urls,
                            platform: $platform
                        },
                        target: {
                            targetType: $platform
                        }
                    }
                }')
        fi
    fi

    # Make API call for this platform
    echo "Posting to: ${platform} (Account ID: ${ACCOUNT_ID})"
    echo "Content: ${CONTENT}"
    [ -n "$SCHEDULE_TIME" ] && echo "Scheduled for: ${SCHEDULE_TIME}"
    echo ""

    RESPONSE=$(curl -s -X POST "${BASE_URL}/v2/posts" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD")

    # Check response
    if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
        echo "Error posting to ${platform}: $(echo "$RESPONSE" | jq -r '.error')"
    else
        echo "Success posting to ${platform}!"
        echo "$RESPONSE" | jq .
    fi
    echo "---"
done

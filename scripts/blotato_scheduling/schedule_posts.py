#!/usr/bin/env python3
import json
import requests
import time

# Load config
with open('.claude/skills/blotato-posting/config.json') as f:
    config = json.load(f)

API_KEY = config['api_key']
BASE_URL = config['base_url']
ACCOUNT_IDS = config['account_ids']

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Load schedule
with open('posting_schedule.json') as f:
    schedule = json.load(f)

print(f"Scheduling {len(schedule)} videos via Blotato API...")
print("="*60)

results = []
errors = []

for idx, item in enumerate(schedule, 1):
    video = item['video']
    platform = item['platform']
    scheduled_time = item['scheduled_time']
    account_id = ACCOUNT_IDS[platform]

    # Get caption based on platform
    if video.get('platform_captions') and platform in video['platform_captions']:
        caption = video['platform_captions'][platform]
    elif video.get('caption'):
        caption = video['caption']
    else:
        # Generic caption
        caption = f"Check this out! 🔥"

    # Get video URL from Klap (stored in metadata)
    # We need to find the video URL from the metadata
    project = video['project']
    filename = video['filename']

    # Read the metadata file to get video URL
    import os
    metadata_path = f"$CONTENT_DIR/ClipShorts/{project}/klap_results.json"

    with open(metadata_path) as f:
        metadata = json.load(f)

    # Find this video in the metadata
    video_url = None
    for short in metadata['shorts']:
        short_filename = short.get('filename') or short.get('file')
        if short_filename == filename:
            video_url = short.get('video_url')
            break

    if not video_url:
        print(f"❌ Error: No video URL found for {filename}")
        errors.append({'video': filename, 'error': 'No video URL'})
        continue

    print(f"\n{idx}/{len(schedule)} - Scheduling {platform.upper()}")
    print(f"   Video: {filename} (Score: {video['score']})")
    print(f"   Time: {scheduled_time}")
    print(f"   Caption: {caption[:60]}...")

    # Build payload based on platform
    payload = {
        'post': {
            'accountId': account_id,
            'content': {
                'text': caption,
                'mediaUrls': [video_url],
                'platform': platform
            },
            'target': {
                'targetType': platform
            }
        },
        'scheduledTime': scheduled_time
    }

    # Platform-specific configurations
    if platform == 'youtube':
        # YouTube Shorts
        payload['post']['target'].update({
            'title': caption[:100],  # YouTube title max 100 chars
            'privacyStatus': 'public',
            'shouldNotifySubscribers': False
        })
    elif platform == 'tiktok':
        # TikTok
        payload['post']['target'].update({
            'privacyLevel': 'PUBLIC_TO_EVERYONE',
            'disabledComments': False,
            'disabledDuet': False,
            'disabledStitch': False,
            'isBrandedContent': False,
            'isYourBrand': False,
            'isAiGenerated': True
        })
    elif platform == 'instagram':
        # Instagram Reels - this is the key part!
        payload['post']['target'].update({
            'shareToFeed': True,  # Share Reel to feed
            'isReel': True  # Mark as Reel (this may be the key field)
        })

    # Make API call
    try:
        response = requests.post(
            f'{BASE_URL}/v2/posts',
            headers=headers,
            json=payload
        )

        if response.status_code == 200 or response.status_code == 201:
            result_data = response.json()
            submission_id = result_data.get('id') or result_data.get('submissionId')

            print(f"   ✅ Scheduled! ID: {submission_id}")

            results.append({
                'index': idx,
                'platform': platform,
                'filename': filename,
                'score': video['score'],
                'scheduled_time': scheduled_time,
                'submission_id': submission_id,
                'status': 'scheduled'
            })
        else:
            error_msg = response.text
            print(f"   ❌ Error: {error_msg}")
            errors.append({
                'video': filename,
                'platform': platform,
                'error': error_msg
            })

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        errors.append({
            'video': filename,
            'platform': platform,
            'error': str(e)
        })

    # Rate limiting - wait 1 second between posts
    time.sleep(1)

print("\n\n" + "="*60)
print("SCHEDULING COMPLETE")
print("="*60)
print(f"Successfully scheduled: {len(results)}")
print(f"Errors: {len(errors)}")

if results:
    print("\nBreakdown by platform:")
    for platform in ['tiktok', 'instagram', 'youtube']:
        count = sum(1 for r in results if r['platform'] == platform)
        if count > 0:
            print(f"  {platform.capitalize()}: {count} posts")

if errors:
    print("\nErrors:")
    for error in errors:
        print(f"  - {error['video']} ({error['platform']}): {error['error']}")

# Save results
with open('scheduling_results.json', 'w') as f:
    json.dump({
        'scheduled': results,
        'errors': errors,
        'total': len(schedule),
        'success_count': len(results),
        'error_count': len(errors)
    }, f, indent=2)

print("\n✓ Results saved to scheduling_results.json")

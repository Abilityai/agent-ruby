#!/usr/bin/env python3
import json
import requests
import subprocess
import time
import os

# Load config
with open('.claude/skills/blotato-posting/config.json') as f:
    config = json.load(f)

API_KEY = config['api_key']
BASE_URL = config['base_url']
ACCOUNT_IDS = config['account_ids']

# Cloudinary config
CLOUDINARY_CLOUD = "dfs5yfioa"
CLOUDINARY_API_KEY = "476858566113846"
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')  # Set if needed

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Load schedule
with open('posting_schedule.json') as f:
    schedule = json.load(f)

# Load already scheduled results to skip
scheduled_ids = []
if os.path.exists('scheduling_results.json'):
    with open('scheduling_results.json') as f:
        prev_results = json.load(f)
        scheduled_ids = [r['index'] for r in prev_results.get('scheduled', [])]

print(f"Scheduling {len(schedule)} videos...")
print(f"Already scheduled: {len(scheduled_ids)}")
print("="*60)

results = []
errors = []
cloudinary_uploads = {}

for idx, item in enumerate(schedule, 1):
    if idx in scheduled_ids:
        print(f"\n{idx}/{len(schedule)} - Skipping (already scheduled)")
        continue

    video = item['video']
    platform = item['platform']
    scheduled_time = item['scheduled_time']
    account_id = ACCOUNT_IDS[platform]

    # Get caption
    if video.get('platform_captions') and platform in video['platform_captions']:
        caption = video['platform_captions'][platform]
    elif video.get('caption'):
        caption = video['caption']
    else:
        caption = "Check this out! 🔥"

    # Get video URL
    project = video['project']
    filename = video['filename']
    video_path = video['path']

    # Read metadata to get Klap URL
    metadata_path = f"/Users/eugene/Library/CloudStorage/GoogleDrive-eugene@ability.ai/My Drive/Eugene Personal Brand/ClipShorts/{project}/klap_results.json"

    try:
        with open(metadata_path) as f:
            metadata = json.load(f)
    except:
        print(f"❌ Error reading metadata for {filename}")
        errors.append({'video': filename, 'platform': platform, 'error': 'Metadata not found'})
        continue

    # Find video URL
    video_url = None
    for short in metadata['shorts']:
        short_filename = short.get('filename') or short.get('file')
        if short_filename == filename:
            video_url = short.get('video_url')
            break

    if not video_url:
        print(f"❌ No video URL for {filename}")
        errors.append({'video': filename, 'platform': platform, 'error': 'No video URL'})
        continue

    # For TikTok, we need to use Cloudinary instead of Klap URLs
    if platform == 'tiktok':
        # Check if already uploaded
        if video_path not in cloudinary_uploads:
            print(f"\n{idx}/{len(schedule)} - Uploading to Cloudinary for TikTok")
            print(f"   Video: {filename}")

            # For now, skip TikTok and note it needs upload
            print(f"   ⏭️  Skipping TikTok (needs Cloudinary upload)")
            errors.append({
                'video': filename,
                'platform': platform,
                'error': 'TikTok needs Cloudinary upload - use manual upload'
            })
            continue
    else:
        # Instagram and YouTube can use Klap URLs
        pass

    print(f"\n{idx}/{len(schedule)} - Scheduling {platform.upper()}")
    print(f"   Video: {filename} (Score: {video['score']})")
    print(f"   Time: {scheduled_time}")
    print(f"   Caption: {caption[:60]}...")

    # Build payload
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

    # Platform-specific configs
    if platform == 'youtube':
        payload['post']['target'].update({
            'title': caption[:100],
            'privacyStatus': 'public',
            'shouldNotifySubscribers': False
        })
    elif platform == 'instagram':
        payload['post']['target'].update({
            'shareToFeed': True,
            'isReel': True  # MARK AS REEL!
        })

    # Schedule
    try:
        response = requests.post(
            f'{BASE_URL}/v2/posts',
            headers=headers,
            json=payload
        )

        if response.status_code in [200, 201]:
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
            error_msg = response.text[:200]
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

    time.sleep(1)

print("\n\n" + "="*60)
print("SCHEDULING COMPLETE")
print("="*60)
print(f"Successfully scheduled: {len(results)}")
print(f"Errors/Skipped: {len(errors)}")

if results:
    print("\nBreakdown by platform:")
    for platform in ['tiktok', 'instagram', 'youtube']:
        count = sum(1 for r in results if r['platform'] == platform)
        if count > 0:
            print(f"  {platform.capitalize()}: {count} posts")

if errors:
    tiktok_count = sum(1 for e in errors if e.get('platform') == 'tiktok')
    print(f"\nTikTok videos need manual Cloudinary upload: {tiktok_count}")

# Save results
with open('final_scheduling_results.json', 'w') as f:
    json.dump({
        'scheduled': results,
        'errors': errors,
        'total': len(schedule),
        'success_count': len(results),
        'error_count': len(errors)
    }, f, indent=2)

print("\n✓ Results saved to final_scheduling_results.json")

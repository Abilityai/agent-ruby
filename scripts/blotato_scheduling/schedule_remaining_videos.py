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

# Dropbox URLs (change dl=0 to dl=1 for direct download)
dropbox_videos = {
    'short_01_score_88.mp4': 'https://www.dropbox.com/scl/fi/r1p4wj2umdciosgy80wrx/short_01_score_88.mp4?rlkey=k5wb505yhbxdo24qx12ftonv4&dl=1',
    'short_02_score_85.mp4': 'https://www.dropbox.com/scl/fi/gw3975zu429mtdm5721dt/short_02_score_85.mp4?rlkey=00tsh8siz5sdv4a9k9gvtsecd&dl=1',
    'short_04_score_82.mp4': 'https://www.dropbox.com/scl/fi/lrews4hj6o2akuvh8yr0k/short_04_score_82.mp4?rlkey=ct70t2wk8mp0ijedtl1rcky13&dl=1',
    'short_05_score_74.mp4': 'https://www.dropbox.com/scl/fi/xgn6qqbw3fk97feedvsxy/short_05_score_74.mp4?rlkey=3nbuu0gz64epwipum8w3umbab&dl=1',
    'short_06_score_62.mp4': 'https://www.dropbox.com/scl/fi/fl1c57f2x4mxpui9pyjwb/short_06_score_62.mp4?rlkey=ke3kfl8amhtao6z3sr2p8mdvi&dl=1',
}

print("Step 1: Uploading Dropbox videos to Blotato...")
print("="*60)

blotato_urls = {}

for filename, dropbox_url in dropbox_videos.items():
    print(f"\nUploading: {filename}")
    print(f"  From: {dropbox_url[:60]}...")

    try:
        response = requests.post(
            f'{BASE_URL}/v2/media',
            headers=headers,
            json={'url': dropbox_url}
        )

        if response.status_code in [200, 201]:
            result = response.json()
            blotato_url = result.get('url')
            blotato_urls[filename] = blotato_url
            print(f"  ✅ Blotato URL: {blotato_url}")
        else:
            print(f"  ❌ Error: {response.text[:100]}")

    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")

    time.sleep(2)  # Wait longer for large files

print(f"\n✓ Uploaded {len(blotato_urls)} videos to Blotato")

# Load schedule to get these videos
with open('posting_schedule.json') as f:
    schedule = json.load(f)

# Load metadata for captions
metadata_path = "/Users/eugene/Library/CloudStorage/GoogleDrive-eugene@ability.ai/My Drive/Eugene Personal Brand/ClipShorts/vide_no_subs_2/klap_results.json"
with open(metadata_path) as f:
    metadata = json.load(f)

# Map filenames to metadata
video_metadata = {}
for short in metadata['shorts']:
    short_filename = short.get('filename') or short.get('file')
    video_metadata[short_filename] = short

print("\n\nStep 2: Scheduling remaining posts...")
print("="*60)

results = []
errors = []

# Find these videos in the schedule
for item in schedule:
    video = item['video']
    filename = video['filename']
    platform = item['platform']
    scheduled_time = item['scheduled_time']

    if filename not in blotato_urls:
        continue  # Skip videos we didn't upload

    video_url = blotato_urls[filename]
    account_id = ACCOUNT_IDS[platform]

    # Get caption from metadata
    if filename in video_metadata:
        meta = video_metadata[filename]
        platform_captions = meta.get('platform_captions', {})

        if platform in platform_captions:
            caption = platform_captions[platform]
        elif meta.get('title'):
            caption = meta['title']
        else:
            caption = "Check this out! 🔥"
    else:
        caption = "Check this out! 🔥"

    print(f"\nScheduling {platform.upper()}")
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
            'isReel': True
        })
    elif platform == 'tiktok':
        payload['post']['target'].update({
            'privacyLevel': 'PUBLIC_TO_EVERYONE',
            'disabledComments': False,
            'disabledDuet': False,
            'disabledStitch': False,
            'isBrandedContent': False,
            'isYourBrand': False,
            'isAiGenerated': True
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
                'platform': platform,
                'filename': filename,
                'score': video['score'],
                'scheduled_time': scheduled_time,
                'submission_id': submission_id,
                'caption': caption,
                'status': 'scheduled'
            })
        else:
            error_msg = response.text[:200]
            print(f"   ❌ Error: {error_msg}")
            errors.append({'video': filename, 'platform': platform, 'error': error_msg})

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        errors.append({'video': filename, 'platform': platform, 'error': str(e)})

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

# Save results
with open('remaining_videos_results.json', 'w') as f:
    json.dump({
        'blotato_urls': blotato_urls,
        'scheduled': results,
        'errors': errors,
        'success_count': len(results),
        'error_count': len(errors)
    }, f, indent=2)

print("\n✓ Results saved to remaining_videos_results.json")

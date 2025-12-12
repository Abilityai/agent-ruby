#!/usr/bin/env python3
import json
import requests
import time

# Load config
with open('.claude/skills/blotato-posting/config.json') as f:
    config = json.load(f)

API_KEY = config['api_key']
BASE_URL = config['base_url']
ACCOUNT_ID = config['account_ids']['tiktok']

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# Cloudinary URLs
cloudinary_urls = {
    'short_01_score_90.mp4': 'https://res.cloudinary.com/dfs5yfioa/video/upload/v1763849176/klap_shorts/arp8d4imwu79jyiqkt1e.mp4',
    'short_02_score_86.mp4': 'https://res.cloudinary.com/dfs5yfioa/video/upload/v1763849181/klap_shorts/wieqpvbe4ginluyfbq3l.mp4',
    'short_02_score_82.mp4': 'https://res.cloudinary.com/dfs5yfioa/video/upload/v1763849193/klap_shorts/btjuuudedfwvdoriukqx.mp4',
    'short_03_score_78.mp4': 'https://res.cloudinary.com/dfs5yfioa/video/upload/v1763849201/klap_shorts/zb46wsrtngtveypzxfna.mp4',
    'short_05_score_78.mp4': 'https://res.cloudinary.com/dfs5yfioa/video/upload/v1763849231/klap_shorts/pevi5ikkjz3ozjol9jg9.mp4',
}

print("Step 1: Uploading to Blotato media endpoint...")
print("="*60)

blotato_urls = {}

for filename, cloudinary_url in cloudinary_urls.items():
    print(f"\nUploading: {filename}")
    print(f"  From: {cloudinary_url[:60]}...")

    try:
        response = requests.post(
            f'{BASE_URL}/v2/media',
            headers=headers,
            json={'url': cloudinary_url}
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

    time.sleep(1)

print(f"\n✓ Uploaded {len(blotato_urls)} videos to Blotato")

# Now schedule TikTok posts
print("\n\nStep 2: Scheduling TikTok posts...")
print("="*60)

# Load schedule
with open('posting_schedule.json') as f:
    schedule = json.load(f)

tiktok_posts = [item for item in schedule if item['platform'] == 'tiktok']

results = []
errors = []

for idx, item in enumerate(tiktok_posts, 1):
    video = item['video']
    filename = video['filename']
    scheduled_time = item['scheduled_time']

    if filename not in blotato_urls:
        print(f"\n{idx}/{len(tiktok_posts)} - Skipping {filename} (no Blotato URL)")
        errors.append({'video': filename, 'error': 'No Blotato URL'})
        continue

    video_url = blotato_urls[filename]

    # Get caption
    if video.get('platform_captions') and 'tiktok' in video['platform_captions']:
        caption = video['platform_captions']['tiktok']
    elif video.get('caption'):
        caption = video['caption']
    else:
        caption = "Check this out! 🔥 #AI #Tech"

    print(f"\n{idx}/{len(tiktok_posts)} - Scheduling TikTok")
    print(f"   Video: {filename} (Score: {video['score']})")
    print(f"   Time: {scheduled_time}")
    print(f"   Caption: {caption[:60]}...")

    # Build payload
    payload = {
        'post': {
            'accountId': ACCOUNT_ID,
            'content': {
                'text': caption,
                'mediaUrls': [video_url],
                'platform': 'tiktok'
            },
            'target': {
                'targetType': 'tiktok',
                'privacyLevel': 'PUBLIC_TO_EVERYONE',
                'disabledComments': False,
                'disabledDuet': False,
                'disabledStitch': False,
                'isBrandedContent': False,
                'isYourBrand': False,
                'isAiGenerated': True
            }
        },
        'scheduledTime': scheduled_time
    }

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
                'platform': 'tiktok',
                'filename': filename,
                'score': video['score'],
                'scheduled_time': scheduled_time,
                'submission_id': submission_id,
                'status': 'scheduled'
            })
        else:
            error_msg = response.text[:200]
            print(f"   ❌ Error: {error_msg}")
            errors.append({'video': filename, 'error': error_msg})

    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        errors.append({'video': filename, 'error': str(e)})

    time.sleep(1)

print("\n\n" + "="*60)
print("TIKTOK SCHEDULING COMPLETE")
print("="*60)
print(f"Successfully scheduled: {len(results)}")
print(f"Errors/Skipped: {len(errors)}")

# Save results
with open('tiktok_final_results.json', 'w') as f:
    json.dump({
        'blotato_urls': blotato_urls,
        'scheduled': results,
        'errors': errors,
        'total': len(tiktok_posts),
        'success_count': len(results),
        'error_count': len(errors)
    }, f, indent=2)

print("\n✓ Results saved to tiktok_final_results.json")

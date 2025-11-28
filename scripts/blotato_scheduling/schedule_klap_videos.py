#!/usr/bin/env python3
import json
import requests
from datetime import datetime, timedelta

# Load config
with open('.claude/skills/blotato-posting/config.json') as f:
    config = json.load(f)

API_KEY = config['api_key']
BASE_URL = config['base_url']
ACCOUNT_IDS = config['account_ids']

# Load schedule
with open('posting_schedule.json') as f:
    schedule = json.load(f)

print(f"Scheduling {len(schedule)} videos...")
print("="*60)

results = []

for idx, item in enumerate(schedule, 1):
    video = item['video']
    platform = item['platform']
    scheduled_time = item['scheduled_time']

    # Get caption based on platform
    if video['platform_captions'] and platform in video['platform_captions']:
        caption = video['platform_captions'][platform]
    elif video['caption']:
        caption = video['caption']
    else:
        caption = f"Check this out! 🔥 #{platform}"

    # Get video URL - use Klap URL if available, otherwise local path
    # For now, we'll upload to Cloudinary first
    video_path = video['path']

    print(f"\n{idx}. Scheduling for {platform.upper()}")
    print(f"   Video: {video['filename']} (Score: {video['score']})")
    print(f"   Time: {scheduled_time}")
    print(f"   Caption: {caption[:80]}...")

    # Upload to Cloudinary first to get URL
    # We'll skip the actual upload for now and just prepare the structure

    # Build payload based on platform
    account_id = ACCOUNT_IDS[platform]

    # For now, let's just print what we would schedule
    # We need to upload videos to Cloudinary first

    result = {
        'index': idx,
        'platform': platform,
        'video_path': video_path,
        'score': video['score'],
        'caption': caption,
        'scheduled_time': scheduled_time,
        'account_id': account_id,
        'status': 'pending_upload'
    }

    results.append(result)

print("\n\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total videos to schedule: {len(results)}")
print(f"TikTok: {sum(1 for r in results if r['platform'] == 'tiktok')}")
print(f"Instagram: {sum(1 for r in results if r['platform'] == 'instagram')}")
print(f"YouTube: {sum(1 for r in results if r['platform'] == 'youtube')}")

# Save results
with open('schedule_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n✓ Schedule prepared. Ready to upload and post.")
print("\nNext steps:")
print("1. Upload videos to Cloudinary to get URLs")
print("2. Schedule posts via Blotato API with proper platform configs:")
print("   - Instagram: Set as Reels")
print("   - YouTube: Set as Shorts")
print("   - TikTok: Standard video post")

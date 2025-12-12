#!/usr/bin/env python3
import os
import json
from datetime import datetime, timedelta

CLIP_SHORTS_DIR = "$CONTENT_DIR/ClipShorts"

# Collect all videos with their scores
all_videos = []

for folder in os.listdir(CLIP_SHORTS_DIR):
    folder_path = os.path.join(CLIP_SHORTS_DIR, folder)
    if not os.path.isdir(folder_path):
        continue

    metadata_path = os.path.join(folder_path, "klap_results.json")
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            data = json.load(f)
            for short in data.get('shorts', []):
                # Handle both 'filename' and 'file' keys
                filename = short.get('filename') or short.get('file')
                video_path = os.path.join(folder_path, filename)

                # Get caption from multiple possible locations
                caption = short.get('caption', '')
                if not caption and 'title' in short:
                    caption = short['title']

                all_videos.append({
                    'path': video_path,
                    'filename': filename,
                    'project': folder,
                    'score': short['virality_score'],
                    'caption': caption,
                    'platform_captions': short.get('platform_captions', {})
                })

# Sort by virality score (descending)
all_videos.sort(key=lambda x: x['score'], reverse=True)

print(f"Total videos: {len(all_videos)}\n")
print("Top 10 videos by virality score:")
print("="*60)
for i, video in enumerate(all_videos[:10], 1):
    print(f"{i}. Score {video['score']} - {video['project']}/{video['filename']}")

# Create posting schedule for next 7 days
start_date = datetime.now() + timedelta(days=1)
start_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)

schedule = []
video_idx = 0

# Posting times per day
posting_times = [
    {"hour": 10, "minute": 0, "platform": "tiktok"},
    {"hour": 14, "minute": 0, "platform": "instagram"},
    {"hour": 17, "minute": 0, "platform": "youtube"},
    {"hour": 18, "minute": 0, "platform": "tiktok"},
]

for day in range(7):
    current_date = start_date + timedelta(days=day)

    for time_slot in posting_times:
        if video_idx >= len(all_videos):
            break

        post_time = current_date.replace(hour=time_slot['hour'], minute=time_slot['minute'])

        schedule.append({
            'video': all_videos[video_idx],
            'platform': time_slot['platform'],
            'scheduled_time': post_time.isoformat(),
            'day': day + 1
        })

        video_idx += 1

    if video_idx >= len(all_videos):
        break

print(f"\n\nSchedule created for {len(schedule)} posts over {max(s['day'] for s in schedule)} days")
print("\nSchedule breakdown:")
print("="*60)

for platform in ['tiktok', 'instagram', 'youtube']:
    count = sum(1 for s in schedule if s['platform'] == platform)
    print(f"{platform.capitalize()}: {count} posts")

# Save schedule
with open('posting_schedule.json', 'w') as f:
    json.dump(schedule, f, indent=2)

print("\n✓ Schedule saved to posting_schedule.json")

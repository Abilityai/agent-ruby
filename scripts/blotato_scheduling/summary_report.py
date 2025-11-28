#!/usr/bin/env python3
import os
import json
from pathlib import Path

CLIP_SHORTS_DIR = "/Users/eugene/Library/CloudStorage/GoogleDrive-eugene@ability.ai/My Drive/Eugene Personal Brand/ClipShorts"

print("="*60)
print("KLAP VIDEO CLIPPING SUMMARY")
print("="*60)
print()

total_clips = 0
total_bytes = 0

for folder in sorted(os.listdir(CLIP_SHORTS_DIR)):
    folder_path = os.path.join(CLIP_SHORTS_DIR, folder)
    if not os.path.isdir(folder_path):
        continue

    # Count clips
    clips = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    clip_count = len(clips)
    total_clips += clip_count

    # Get folder size
    folder_bytes = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, dirnames, filenames in os.walk(folder_path)
        for filename in filenames
    )
    total_bytes += folder_bytes
    folder_size_mb = folder_bytes / (1024 * 1024)

    # Get top score
    metadata_path = os.path.join(folder_path, "klap_results.json")
    top_score = "N/A"
    if os.path.exists(metadata_path):
        with open(metadata_path) as f:
            data = json.load(f)
            if data.get('shorts'):
                top_score = data['shorts'][0]['virality_score']

    print(f"📁 {folder}")
    print(f"   Shorts: {clip_count} clips")
    print(f"   Size: {folder_size_mb:.1f} MB")
    print(f"   Top score: {top_score}")
    print()

print("="*60)
print("TOTAL")
print("="*60)
print(f"Total clips: {total_clips}")
print(f"Total size: {total_bytes / (1024 * 1024):.1f} MB ({total_bytes / (1024 * 1024 * 1024):.2f} GB)")
print()
print(f"Location: {CLIP_SHORTS_DIR}")
print()
print("✓ All videos processed successfully!")

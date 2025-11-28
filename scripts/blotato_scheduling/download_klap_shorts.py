#!/usr/bin/env python3
import requests
import time
import json
import os
from pathlib import Path

API_KEY = "kak_K1eQjUgRXr7l7vKDzYOO6u5u"
BASE_URL = "https://api.klap.app/v2"
CLIP_SHORTS_DIR = "/Users/eugene/Library/CloudStorage/GoogleDrive-eugene@ability.ai/My Drive/Eugene Personal Brand/ClipShorts"

tasks = [
    {"id": "8HL9qHpyeO1fISca", "folder": "UUk2UHxJ", "name": "Data-Privacy_FINAL"},
    {"id": "1nEGBW04aCnBjGuK", "folder": "vCWNJyd9", "name": "video_no_subs_1"},
    {"id": "DHuQLMdzZxIJphAU", "folder": "YmFzKeSf", "name": "short"},
    {"id": "3IMgjJQT5r4rQkG4", "folder": "RHghepMF", "name": "vide_no_subs_2"}
]

headers = {"Authorization": f"Bearer {API_KEY}"}

os.makedirs(CLIP_SHORTS_DIR, exist_ok=True)

for task in tasks:
    print(f"\n{'='*60}")
    print(f"Processing: {task['name']}")
    print(f"{'='*60}\n")

    # Create subfolder for this video
    video_folder = os.path.join(CLIP_SHORTS_DIR, task['name'])
    os.makedirs(video_folder, exist_ok=True)

    # Get project details
    response = requests.get(f"{BASE_URL}/projects/{task['folder']}", headers=headers)
    shorts = response.json()

    # Handle if response is a dict with 'projects' key or direct list
    if isinstance(shorts, dict):
        shorts = shorts.get('projects', [])

    print(f"Found {len(shorts)} shorts for {task['name']}")

    # Sort by virality score (descending)
    shorts_sorted = sorted(shorts, key=lambda x: x.get('virality_score', 0), reverse=True)

    results = []

    for idx, short in enumerate(shorts_sorted, 1):
        project_id = short['id']
        folder_id = task['folder']
        score = short.get('virality_score', 0)
        caption = short.get('caption', '')

        print(f"\n  Short {idx}: Score {score} - Exporting...")

        # Request export
        export_response = requests.post(
            f"{BASE_URL}/projects/{folder_id}/{project_id}/exports",
            headers=headers,
            json={}
        )
        export_data = export_response.json()
        export_id = export_data['id']

        # Poll for export completion
        export_ready = False
        while not export_ready:
            export_status_response = requests.get(
                f"{BASE_URL}/projects/{folder_id}/{project_id}/exports/{export_id}",
                headers=headers
            )
            export_status = export_status_response.json()

            if export_status.get('status') == 'ready':
                export_ready = True
                video_url = export_status['src_url']

                # Download video
                filename = f"short_{idx:02d}_score_{score}.mp4"
                filepath = os.path.join(video_folder, filename)

                print(f"  Downloading to: {filename}")
                video_response = requests.get(video_url)
                with open(filepath, 'wb') as f:
                    f.write(video_response.content)

                results.append({
                    "filename": filename,
                    "virality_score": score,
                    "caption": caption,
                    "video_url": video_url
                })

                print(f"  ✓ Saved: {filename}")
            else:
                time.sleep(2)

    # Save metadata
    metadata_path = os.path.join(video_folder, "klap_results.json")
    with open(metadata_path, 'w') as f:
        json.dump({
            "source_video": task['name'],
            "total_shorts": len(results),
            "shorts": results
        }, f, indent=2)

    print(f"\n  ✓ Metadata saved: klap_results.json")
    print(f"  ✓ All {len(results)} shorts downloaded to: {video_folder}")

print(f"\n\n{'='*60}")
print("✓ ALL VIDEOS PROCESSED SUCCESSFULLY")
print(f"{'='*60}")
print(f"\nLocation: {CLIP_SHORTS_DIR}")

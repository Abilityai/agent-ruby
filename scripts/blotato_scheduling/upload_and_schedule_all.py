#!/usr/bin/env python3
import json
import requests
import time
import os

# Load config
with open('.claude/skills/blotato-posting/config.json') as f:
    config = json.load(f)

API_KEY = config['api_key']
BASE_URL = config['base_url']
ACCOUNT_IDS = config['account_ids']

# Cloudinary config (from MCP)
CLOUDINARY_CLOUD = "dfs5yfioa"

# Load schedule
with open('posting_schedule.py', 'w') as f:
    schedule = json.load(f)

print("Step 1: Uploading all videos to Cloudinary...")
print("="*60)

# Upload all unique videos to Cloudinary
uploaded_videos = {}

for item in schedule:
    video = item['video']
    video_path = video['path']

    if video_path in uploaded_videos:
        continue  # Already uploaded

    filename = video['filename']
    project = video['project']

    print(f"\nUploading: {filename}")
    print(f"  From: {project}")

    # We'll use the Cloudinary MCP to upload
    # For now, let's prepare the list and upload via MCP tool

    uploaded_videos[video_path] = {
        'local_path': video_path,
        'filename': filename,
        'project': project,
        'status': 'pending'
    }

print(f"\n✓ Need to upload {len(uploaded_videos)} unique videos")

# Save the upload list
with open('videos_to_upload.json', 'w') as f:
    json.dump(list(uploaded_videos.values()), f, indent=2)

print("\n✓ Video list saved to videos_to_upload.json")
print("\nNext: I'll upload these to Cloudinary using the MCP tool")

#!/usr/bin/env python3
"""
Klap API Integration for Ruby
Converts long-form videos into viral shorts
"""

import os
import requests
import time
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Load environment variables from .env
def load_env():
    """Load .env file from project root"""
    script_dir = Path(__file__).parent
    env_file = script_dir.parent / '.env'

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    else:
        print(f"Warning: .env file not found at {env_file}")

load_env()

class KlapAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.klap.app/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_shorts_task(
        self,
        video_url: str,
        language: str = "en",
        max_duration: int = 60,
        target_clip_count: int = 5,
        captions: bool = True,
        reframe: bool = True,
        emojis: bool = False,
        intro_title: bool = False
    ) -> Dict:
        """
        Submit video for shorts generation

        Args:
            video_url: YouTube, S3, GCS, or public HTTP/HTTPS URL
            language: Source language code (auto-detects if not specified)
            max_duration: Max clip length in seconds (1-180)
            target_clip_count: Desired number of clips (default 10)
            captions: Add dynamic captions
            reframe: AI reframing to vertical
            emojis: Add emojis to captions
            intro_title: Add intro title to clips

        Returns:
            Task object with id and status
        """
        payload = {
            "source_video_url": video_url,
            "language": language,
            "max_duration": max_duration,
            "target_clip_count": target_clip_count,
            "editing_options": {
                "captions": captions,
                "reframe": reframe,
                "emojis": emojis,
                "intro_title": intro_title
            }
        }

        response = requests.post(
            f"{self.base_url}/tasks/video-to-shorts",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_task_status(self, task_id: str) -> Dict:
        """Poll task status"""
        response = requests.get(
            f"{self.base_url}/tasks/{task_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 30,
        max_wait: int = 1800
    ) -> Dict:
        """
        Wait for task to complete

        Args:
            task_id: Task ID to monitor
            poll_interval: Seconds between status checks
            max_wait: Maximum wait time in seconds

        Returns:
            Completed task object
        """
        start_time = time.time()

        while True:
            task = self.get_task_status(task_id)
            status = task['status']

            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] Status: {status}")

            if status == "ready":
                return task
            elif status == "error":
                raise Exception(f"Task failed: {task.get('error_code')}")
            elif elapsed > max_wait:
                raise TimeoutError(f"Task timeout after {max_wait}s")

            time.sleep(poll_interval)

    def get_shorts(self, folder_id: str) -> List[Dict]:
        """
        Get all generated shorts from folder

        Returns list of project objects with virality scores
        """
        response = requests.get(
            f"{self.base_url}/projects/{folder_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def export_short(
        self,
        folder_id: str,
        project_id: str,
        watermark_url: Optional[str] = None
    ) -> Dict:
        """
        Export a short for download

        Args:
            folder_id: Output folder ID from task
            project_id: Specific short to export
            watermark_url: Optional watermark image URL

        Returns:
            Export task object
        """
        payload = {}
        if watermark_url:
            payload["watermark"] = {
                "src_url": watermark_url,
                "pos_x": 0.5,
                "pos_y": 0.5,
                "scale": 1
            }

        response = requests.post(
            f"{self.base_url}/projects/{folder_id}/{project_id}/exports",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_export_status(
        self,
        folder_id: str,
        project_id: str,
        export_id: str
    ) -> Dict:
        """Get export status and download URL"""
        response = requests.get(
            f"{self.base_url}/projects/{folder_id}/{project_id}/exports/{export_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def wait_for_export(
        self,
        folder_id: str,
        project_id: str,
        export_id: str,
        poll_interval: int = 10,
        max_wait: int = 300
    ) -> str:
        """
        Wait for export to complete and return download URL
        """
        start_time = time.time()

        while True:
            export = self.get_export_status(folder_id, project_id, export_id)
            status = export['status']

            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}s] Export status: {status}")

            if status == "completed":
                return export['src_url']
            elif status == "error":
                raise Exception(f"Export failed: {export}")
            elif elapsed > max_wait:
                raise TimeoutError(f"Export timeout after {max_wait}s")

            time.sleep(poll_interval)


def main():
    if len(sys.argv) < 2:
        print("Usage: python klap_clipper.py <video_url> [max_clips]")
        print("Example: python klap_clipper.py https://youtube.com/watch?v=xxx 5")
        print("\nNote: API key is loaded from .env file (KLAP_API_KEY)")
        sys.exit(1)

    api_key = os.getenv('KLAP_API_KEY')
    if not api_key:
        print("Error: KLAP_API_KEY not found in .env file")
        sys.exit(1)

    video_url = sys.argv[1]
    max_clips = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    klap = KlapAPI(api_key)

    # Step 1: Submit video
    print(f"\n=== Submitting Video ===")
    print(f"URL: {video_url}")
    print(f"Max clips: {max_clips}")

    task = klap.create_shorts_task(
        video_url=video_url,
        target_clip_count=max_clips,
        max_duration=60,
        captions=True,
        reframe=True
    )

    task_id = task['id']
    folder_id = task['output_id']
    print(f"Task ID: {task_id}")
    print(f"Folder ID: {folder_id}")

    # Step 2: Wait for completion
    print(f"\n=== Processing Video ===")
    completed_task = klap.wait_for_completion(task_id)
    print(f"✓ Processing complete!")

    # Step 3: Get shorts
    print(f"\n=== Generated Shorts ===")
    shorts = klap.get_shorts(folder_id)

    # Sort by virality score
    shorts.sort(key=lambda x: x.get('virality_score', 0), reverse=True)

    print(f"Total shorts: {len(shorts)}")
    print(f"\nTop {min(3, len(shorts))} by virality:")

    for i, short in enumerate(shorts[:3], 1):
        print(f"{i}. Score: {short.get('virality_score', 0)}")
        print(f"   ID: {short['id']}")
        print(f"   Duration: {short.get('duration', 0)}s")

    # Step 4: Export top short
    if shorts:
        top_short = shorts[0]
        print(f"\n=== Exporting Top Short ===")
        print(f"Project ID: {top_short['id']}")

        export_task = klap.export_short(folder_id, top_short['id'])
        export_id = export_task['id']

        download_url = klap.wait_for_export(folder_id, top_short['id'], export_id)

        print(f"\n✓ Export complete!")
        print(f"Download URL: {download_url}")

        # Save results
        results = {
            "task_id": task_id,
            "folder_id": folder_id,
            "shorts": shorts,
            "top_short_url": download_url
        }

        with open('klap_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to klap_results.json")


if __name__ == '__main__':
    main()

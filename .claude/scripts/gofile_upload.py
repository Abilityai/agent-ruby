#!/usr/bin/env python3
"""
GoFile Upload Helper
Uploads media files to GoFile and returns shareable URLs
"""

import sys
import os
import requests
import json
from pathlib import Path

# Load .env file if it exists
def load_env():
    """Load environment variables from .env file"""
    script_dir = Path(__file__).parent
    env_file = script_dir / "../../.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env()

# GoFile credentials (from environment variables)
ACCOUNT_ID = os.getenv("GOFILE_ACCOUNT_ID", "")
API_TOKEN = os.getenv("GOFILE_API_TOKEN", "")
ROOT_FOLDER = os.getenv("GOFILE_ROOT_FOLDER", "")

if not API_TOKEN or not ROOT_FOLDER:
    print("Error: GoFile credentials not set. Please configure .env file.")
    print("Required: GOFILE_API_TOKEN, GOFILE_ROOT_FOLDER")
    sys.exit(1)


def get_upload_server():
    """Get the best GoFile server for uploading"""
    try:
        response = requests.get("https://api.gofile.io/servers")
        response.raise_for_status()
        data = response.json()

        if data["status"] == "ok":
            return data["data"]["servers"][0]["name"]
        else:
            raise Exception("Failed to get upload server")
    except Exception as e:
        print(f"Error getting server: {e}")
        sys.exit(1)


def upload_file(file_path):
    """Upload file to GoFile and return download URL"""

    # Check file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    print(f"Uploading file: {file_name}")
    print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")

    # Get upload server
    print("Getting upload server...")
    server = get_upload_server()
    print(f"Using server: {server}")

    # Upload file
    print("Uploading to GoFile...")
    url = f"https://{server}.gofile.io/contents/uploadfile"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }

    files = {
        "file": open(file_path, "rb")
    }

    data = {
        "folderId": ROOT_FOLDER
    }

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        result = response.json()

        if result["status"] == "ok":
            download_url = result["data"]["downloadPage"]
            file_id = result["data"]["id"]
            size = result["data"]["size"]

            print("\n✅ Upload successful!")
            print(f"Download URL: {download_url}")
            print(f"File ID: {file_id}")
            print(f"Size: {size:,} bytes")
            print("\nUse this URL with Blotato for posting to social media.")
            print("File will auto-delete in 10-30 days.\n")

            return download_url
        else:
            print(f"Error: Upload failed - {result}")
            sys.exit(1)

    except Exception as e:
        print(f"Error uploading file: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 gofile_upload.py <file_path>")
        print("Example: python3 gofile_upload.py /path/to/video.mp4")
        sys.exit(1)

    file_path = sys.argv[1]
    url = upload_file(file_path)
    print(url)


if __name__ == "__main__":
    main()

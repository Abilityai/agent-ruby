#!/usr/bin/env python3
import requests
import time
import json

API_KEY = "kak_K1eQjUgRXr7l7vKDzYOO6u5u"
BASE_URL = "https://api.klap.app/v2"

tasks = [
    {"id": "8HL9qHpyeO1fISca", "folder": "UUk2UHxJ", "name": "Data-Privacy_FINAL"},
    {"id": "1nEGBW04aCnBjGuK", "folder": "vCWNJyd9", "name": "video_no_subs_1"},
    {"id": "DHuQLMdzZxIJphAU", "folder": "YmFzKeSf", "name": "short"},
    {"id": "3IMgjJQT5r4rQkG4", "folder": "RHghepMF", "name": "vide_no_subs_2"}
]

headers = {"Authorization": f"Bearer {API_KEY}"}

print("Checking status of all 4 tasks...\n")

for task in tasks:
    response = requests.get(f"{BASE_URL}/tasks/{task['id']}", headers=headers)
    data = response.json()
    print(f"{task['name']}: {data['status']}")

print("\n" + "="*50)
print("Waiting for all tasks to complete...")
print("="*50 + "\n")

all_ready = False
while not all_ready:
    all_ready = True
    statuses = []

    for task in tasks:
        response = requests.get(f"{BASE_URL}/tasks/{task['id']}", headers=headers)
        data = response.json()
        status = data['status']
        statuses.append(f"{task['name']}: {status}")

        if status != "ready":
            all_ready = False

    print("\r" + " | ".join(statuses), end="", flush=True)

    if not all_ready:
        time.sleep(30)

print("\n\n✓ All tasks complete!")

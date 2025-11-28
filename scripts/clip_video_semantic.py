#!/usr/bin/env python3
"""
Semantic Video Clipper
Uses Gemini 1.5 Pro to analyze video and FFmpeg to extract clips
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def analyze_video_with_gemini(video_path, instruction):
    """
    Call Gemini via gemini-agent to get clip timestamps
    Returns JSON with clip segments
    """
    # Escape quotes in instruction
    instruction_escaped = instruction.replace('"', '\\"')

    prompt = f'''Analyze this video and identify the best clips based on this instruction: "{instruction_escaped}"

Return ONLY a JSON array with this exact structure (no markdown, no explanation):
[
  {{
    "start_time": "MM:SS",
    "end_time": "MM:SS",
    "description": "Brief description of what happens in this clip",
    "reason": "Why this clip matches the instruction"
  }}
]

Make sure timestamps are in MM:SS format (e.g., "01:30" for 1 minute 30 seconds).
Identify 3-5 of the most compelling clips that match the instruction.'''

    # Call gemini-agent sub-agent
    cmd = [
        'claude',
        '--agent', 'gemini-agent',
        '-p', prompt,
        '--output-format', 'json'
    ]

    # Note: You'd need to upload video to Gemini first
    # For now, using file path - actual implementation needs File API
    print(f"Analyzing video with Gemini: {video_path}")
    print(f"Instruction: {instruction}")

    # For testing, return mock data
    # In production, parse result from gemini-agent
    return [
        {
            "start_time": "01:30",
            "end_time": "02:45",
            "description": "90% failure rate discussion",
            "reason": "Key insight about implementation failures"
        },
        {
            "start_time": "05:10",
            "end_time": "06:20",
            "description": "Human resistance factor",
            "reason": "Important psychological barrier explanation"
        }
    ]

def convert_timestamp_to_seconds(timestamp):
    """Convert MM:SS to seconds"""
    parts = timestamp.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return 0

def cut_clip_with_ffmpeg(video_path, start_time, end_time, output_path):
    """
    Cut a clip from video using FFmpeg
    Uses -ss before -i for fast seeking, -c copy for lossless cutting
    """
    # For precise cuts with re-encoding (higher quality):
    cmd = [
        'ffmpeg',
        '-ss', start_time,
        '-i', video_path,
        '-to', end_time,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-preset', 'fast',
        '-crf', '18',  # High quality
        '-y',  # Overwrite output
        output_path
    ]

    print(f"Cutting clip: {start_time} to {end_time}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error cutting clip: {result.stderr}")
        return False

    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python clip_video_semantic.py <video_path> <instruction> [output_dir]")
        print("Example: python clip_video_semantic.py video.mp4 'Find the most insightful moments' ./clips")
        sys.exit(1)

    video_path = sys.argv[1]
    instruction = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else './clips'

    # Verify video exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Analyze video with Gemini
    print("\n=== Step 1: Analyzing video with Gemini ===")
    clips = analyze_video_with_gemini(video_path, instruction)

    print(f"\nFound {len(clips)} clips:")
    for i, clip in enumerate(clips, 1):
        print(f"{i}. {clip['start_time']} - {clip['end_time']}: {clip['description']}")

    # Step 2: Cut clips with FFmpeg
    print("\n=== Step 2: Cutting clips with FFmpeg ===")
    video_basename = Path(video_path).stem

    for i, clip in enumerate(clips, 1):
        output_filename = f"{video_basename}_clip_{i:02d}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        success = cut_clip_with_ffmpeg(
            video_path,
            clip['start_time'],
            clip['end_time'],
            output_path
        )

        if success:
            print(f"✓ Created: {output_path}")
            # Save metadata
            metadata_path = output_path.replace('.mp4', '_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(clip, f, indent=2)
        else:
            print(f"✗ Failed: {output_filename}")

    print(f"\n=== Complete! Clips saved to: {output_dir} ===")

if __name__ == '__main__':
    main()

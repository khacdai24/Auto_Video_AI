# AI Video Generation Pipeline - Project Spec

## Goal

Build an automated AI video generation system.

Input:

- User enters a topic/title

Output:

- Complete rendered video (`final.mp4`)
- Voice narration
- Subtitles
- Multiple scenes
- Video clips merged automatically

------------------------------------------------------------------------

# Overall Architecture

    flowchart TD

    A[User Topic Input]
    -->B[LLM Story Generator]

    B
    -->C[Generate Structured JSON]

    C
    -->D[TTS Voice Generator]

    D
    -->E[Get Audio Duration]

    E
    -->F[Generate Scene Image]

    F
    -->G[Animate Image Into Video]

    G
    -->H[Generate Subtitle]

    H
    -->I[FFmpeg Merge]

    I
    -->J[final.mp4]

------------------------------------------------------------------------

# Step 1: Story Generation

Responsible:

- GPT / Gemini

Task:

Generate structured JSON.

Example:

    {
      "title":"Future City",

      "scenes":[

        {
          "scene_id":1,
          "duration":8,

          "narration":
          "A young boy walks through a futuristic city.",

          "visual_prompt":
          "Cyberpunk city at night with neon lights",

          "camera_motion":
          "slow dolly in",

          "subtitle":
          "A young boy walks through a futuristic city"
        },

        {
          "scene_id":2,
          "duration":7,

          "narration":
          "Flying cars move across the sky.",

          "visual_prompt":
          "Flying cars in futuristic city",

          "camera_motion":
          "tracking shot",

          "subtitle":
          "Flying cars move across the sky"
        }
      ]
    }

Output:

story.json

------------------------------------------------------------------------

# Step 2: Voice Generation

Responsible:

Minimax TTS API

Input:

narration text

Example:

Scene 1 narration:

"A young boy walks through a futuristic city."

Output:

scene_1.mp3

------------------------------------------------------------------------

# Step 3: Calculate Audio Duration

Task:

Read generated mp3 duration.

Python example:

    from pydub import AudioSegment

    audio=AudioSegment.from_mp3(
    "scene_1.mp3"
    )

    duration=audio.duration_seconds

    print(duration)

Save:

    {
    "scene":1,
    "duration":8.25
    }

------------------------------------------------------------------------

# Step 4: Generate Images

Recommended:

Flux

Input:

visual_prompt

Example:

"Cyberpunk city at night"

Output:

scene_1.png

------------------------------------------------------------------------

# Step 5: Convert Image → Video {#step-5-convert-image-video}

Recommended:

Kling

or

Gemini

or

Veo

Input:

scene_1.png

camera_motion

duration

Output:

scene_1.mp4

------------------------------------------------------------------------

# Step 6: Subtitle Generation

Create SRT automatically.

Example:

scene_1.srt

    1
    00:00:00,000 --> 00:00:08,000

    A young boy walks through a futuristic city

------------------------------------------------------------------------

# Step 7: Video Merge

Use:

FFmpeg

Create:

merge.txt

    file 'scene_1.mp4'
    file 'scene_2.mp4'

Merge:

    ffmpeg -f concat -safe 0 -i merge.txt -c copy output.mp4

Add audio:

    ffmpeg \
    -i output.mp4 \
    -i narration.mp3 \
    -c:v copy \
    -c:a aac \
    final.mp4

Burn subtitle:

    ffmpeg \
    -i final.mp4 \
    -vf subtitles=scene_1.srt \
    video_final.mp4

------------------------------------------------------------------------

# Recommended Tech Stack

Backend:

- Python
- FastAPI

Queue:

- Redis
- Celery

Video:

- FFmpeg
- MoviePy

Storage:

- Local storage initially
- AWS S3 later

Database:

- SQLite
- PostgreSQL later

------------------------------------------------------------------------

# Build Phases

## Phase 1 (MVP)

Implement:

Topic → GPT JSON generation → TTS → Subtitle generation → FFmpeg merge

Use static images with zoom effect.

Goal:

Generate first complete video.

------------------------------------------------------------------------

## Phase 2

Implement:

Flux → Kling animation

Goal:

Dynamic AI-generated video scenes.

------------------------------------------------------------------------

## Phase 3

Implement:

- Multiple templates
- Multiple voices
- TikTok auto upload
- YouTube Shorts auto upload
- Facebook auto upload

------------------------------------------------------------------------

# Final Workflow Summary

Topic

↓

GPT Story Generation

↓

Minimax Voice

↓

Flux Image Generation

↓

Kling/Gemini/Veo Animation

↓

Subtitle Generation

↓

FFmpeg Merge

↓

final.mp4

#!/usr/bin/env python3
"""
🎬 AI Video Generation Pipeline — 100% Miễn phí
Tự động tạo video dọc (9:16) từ chủ đề bằng AI.

Sử dụng:
    python main.py --topic "Thành phố tương lai"
    python main.py --topic "Khám phá vũ trụ" --scenes 3
"""
import argparse
import json
import os
import re
import sys
import time
import unicodedata

from config import OUTPUT_DIR, DEFAULT_NUM_SCENES, VIDEO_WIDTH, VIDEO_HEIGHT
from pipeline.story_generator import generate_story
from pipeline.voice_generator import generate_voice
from pipeline.audio_utils import get_audio_duration
from pipeline.image_generator import generate_image, burn_subtitle_to_image
from pipeline.video_animator import animate_image
from pipeline.subtitle_generator import generate_srt
from pipeline.video_merger import merge_videos
from pipeline.title_card import create_intro_card, create_outro_card


def slugify(text):
    """Chuyển text thành slug an toàn cho tên thư mục."""
    # Bỏ dấu tiếng Việt
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Chỉ giữ chữ, số, dấu gạch
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text or "video"


def print_banner():
    """In banner đẹp khi khởi chạy."""
    banner = """
╔══════════════════════════════════════════════════╗
║  🎬  AI Video Generation Pipeline  v2.0         ║
║  📱  Video dọc 9:16 — TikTok/Reels/Shorts       ║
║  💰  100% Miễn phí — Không tốn API              ║
║  🇻🇳  Hỗ trợ tiếng Việt                          ║
╚══════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    parser = argparse.ArgumentParser(
        description="🎬 Tự động tạo video dọc 9:16 bằng AI — 100% miễn phí",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ:
  python main.py --topic "Thành phố tương lai"
  python main.py --topic "Khám phá vũ trụ" --scenes 3
  python main.py --topic "Lịch sử Việt Nam" --scenes 7
        """
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Chủ đề video (tiếng Việt hoặc tiếng Anh)"
    )
    parser.add_argument(
        "--scenes",
        type=int,
        default=DEFAULT_NUM_SCENES,
        help=f"Số lượng cảnh (mặc định: {DEFAULT_NUM_SCENES})"
    )

    args = parser.parse_args()

    print_banner()

    # Nếu không truyền --topic, hỏi trực tiếp
    topic = args.topic
    if not topic:
        topic = input("📝 Nhập chủ đề video: ").strip()
        if not topic:
            print("❌ Chủ đề không được để trống!")
            sys.exit(1)

    num_scenes = args.scenes

    # Tạo thư mục output
    slug = slugify(topic)
    output_dir = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(output_dir, exist_ok=True)

    print(f"📁 Thư mục output: {output_dir}")
    print(f"📝 Chủ đề: {topic}")
    print(f"🎬 Số cảnh: {num_scenes}")
    print(f"📱 Tỷ lệ: 9:16 ({VIDEO_WIDTH}×{VIDEO_HEIGHT})")
    print()

    start_time = time.time()

    # ═══════════════════════════════════════════════════════════
    # STEP 1: Sinh kịch bản
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("📖 STEP 1/8: Sinh kịch bản...")
    print("━" * 50)

    story = generate_story(topic, num_scenes)

    # Lưu story.json
    story_path = os.path.join(output_dir, "story.json")
    with open(story_path, 'w', encoding='utf-8') as f:
        json.dump(story, f, ensure_ascii=False, indent=2)

    print(f"   ✅ Tiêu đề: {story['title']}")
    print(f"   ✅ Số cảnh: {len(story['scenes'])}")
    print(f"   ✅ Đã lưu: story.json")
    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 2: Tạo giọng đọc + tính thời lượng
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🎙️  STEP 2/8: Tạo giọng đọc (edge-tts, +15%)...")
    print("━" * 50)

    for scene in story["scenes"]:
        sid = scene["scene_id"]
        audio_path = os.path.join(output_dir, f"scene_{sid}.mp3")

        print(f"   🎙️  Scene {sid}: \"{scene['narration'][:50]}...\"")
        generate_voice(scene["narration"], audio_path)

        # Tính duration
        duration = get_audio_duration(audio_path)
        scene["actual_duration"] = duration
        print(f"   ✅ scene_{sid}.mp3 ({duration}s)")

    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 3: Tạo Intro/Outro Title Cards
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🎨 STEP 3/8: Tạo Intro & Outro title cards...")
    print("━" * 50)

    intro_image_path = os.path.join(output_dir, "scene_intro.png")
    outro_image_path = os.path.join(output_dir, "scene_outro.png")

    create_intro_card(story["title"], intro_image_path)
    create_outro_card(outro_image_path)

    # Tạo video intro/outro (zoom_in nhẹ, 3 giây)
    intro_video_path = os.path.join(output_dir, "scene_intro.mp4")
    outro_video_path = os.path.join(output_dir, "scene_outro.mp4")

    intro_duration = 3.0
    outro_duration = 3.0

    print("   🎥 Tạo video intro (3s, zoom_in)...")
    animate_image(intro_image_path, intro_video_path, intro_duration, "zoom_in")
    print("   🎥 Tạo video outro (3s, zoom_out)...")
    animate_image(outro_image_path, outro_video_path, outro_duration, "zoom_out")

    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 4: Sinh hình ảnh
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🖼️  STEP 4/8: Sinh hình ảnh dọc 9:16 (Pollinations.ai)...")
    print("━" * 50)

    for scene in story["scenes"]:
        sid = scene["scene_id"]
        image_path = os.path.join(output_dir, f"scene_{sid}.png")

        print(f"   🖼️  Scene {sid}: \"{scene['visual_prompt'][:60]}...\"")
        generate_image(scene["visual_prompt"], image_path)
        burn_subtitle_to_image(image_path, scene["subtitle"])

    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 5: Tạo video từ ảnh (Ken Burns — chỉ zoom)
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🎥 STEP 5/8: Tạo video Ken Burns (chỉ zoom, mượt mà)...")
    print("━" * 50)

    for scene in story["scenes"]:
        sid = scene["scene_id"]
        image_path = os.path.join(output_dir, f"scene_{sid}.png")
        video_path = os.path.join(output_dir, f"scene_{sid}.mp4")

        print(f"   🎥 Scene {sid}: {scene['camera_motion']} ({scene['actual_duration']}s)")
        animate_image(
            image_path, video_path,
            scene["actual_duration"],
            scene["camera_motion"]
        )
        print(f"   ✅ scene_{sid}.mp4")

    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 6: Tạo phụ đề
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("📝 STEP 6/8: Tạo phụ đề SRT...")
    print("━" * 50)

    # Tạo scene list bao gồm intro + scenes + outro
    all_scenes_for_srt = []

    # Intro — phụ đề trống (title card tự có chữ)
    all_scenes_for_srt.append({
        "scene_id": "intro",
        "subtitle": "",
        "actual_duration": intro_duration
    })

    # Các scene chính
    for scene in story["scenes"]:
        all_scenes_for_srt.append(scene)

    # Outro — phụ đề trống
    all_scenes_for_srt.append({
        "scene_id": "outro",
        "subtitle": "",
        "actual_duration": outro_duration
    })

    srt_path = os.path.join(output_dir, "subtitles.srt")
    generate_srt(all_scenes_for_srt, srt_path)
    print(f"   ✅ subtitles.srt")
    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 7: Tạo audio cho intro/outro (im lặng)
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🔇 STEP 7/8: Tạo audio im lặng cho intro/outro...")
    print("━" * 50)

    _create_silent_audio(
        os.path.join(output_dir, "scene_intro.mp3"), intro_duration
    )
    _create_silent_audio(
        os.path.join(output_dir, "scene_outro.mp3"), outro_duration
    )
    print("   ✅ Audio intro/outro (im lặng)")
    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 8: Ghép video hoàn chỉnh
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🔗 STEP 8/8: Ghép video hoàn chỉnh (fade + giọng đọc)...")
    print("━" * 50)

    # Xây dựng danh sách scenes đầy đủ (intro + content + outro)
    full_scenes = []
    full_scenes.append({
        "scene_id": "intro",
        "actual_duration": intro_duration
    })
    for scene in story["scenes"]:
        full_scenes.append(scene)
    full_scenes.append({
        "scene_id": "outro",
        "actual_duration": outro_duration
    })

    final_path = os.path.join(output_dir, "final.mp4")
    merge_videos(full_scenes, output_dir, final_path)

    # Cập nhật story.json với actual_duration
    with open(story_path, 'w', encoding='utf-8') as f:
        json.dump(story, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)

    # ═══════════════════════════════════════════════════════════
    # HOÀN THÀNH!
    # ═══════════════════════════════════════════════════════════
    file_size_mb = os.path.getsize(final_path) / (1024 * 1024)

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  ✅  HOÀN THÀNH! — Video 9:16 Premium           ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"   📁 Video: {final_path}")
    print(f"   📱 Tỷ lệ: 9:16 ({VIDEO_WIDTH}×{VIDEO_HEIGHT})")
    print(f"   📊 Dung lượng: {file_size_mb:.1f} MB")
    print(f"   ⏱️  Thời gian: {minutes}m {seconds}s")
    print(f"   💰 Chi phí: $0")
    print()
    print(f"   ✨ Tính năng: Intro/Outro, Fade transitions,")
    print(f"      Giọng đọc rõ, Bitrate cao")
    print()
    print(f"   👉 Mở video: open \"{final_path}\"")
    print()

    # Dọn dẹp file tạm intro/outro audio
    for tmp in ["scene_intro.mp3", "scene_outro.mp3"]:
        tmp_path = os.path.join(output_dir, tmp)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _create_silent_audio(output_path, duration):
    """Tạo file audio im lặng cho intro/outro."""
    try:
        from pydub import AudioSegment
        silence = AudioSegment.silent(duration=int(duration * 1000))
        silence.export(output_path, format="mp3")
    except Exception as e:
        # Fallback: dùng FFmpeg tạo audio im lặng
        import subprocess
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo',
            '-t', str(duration),
            '-c:a', 'libmp3lame',
            output_path
        ], capture_output=True, check=True)


if __name__ == "__main__":
    main()

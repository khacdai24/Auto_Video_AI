#!/usr/bin/env python3
"""
🎬 AI Video Generation Pipeline v2.1 — 100% Miễn phí
Tự động tạo video dọc (9:16) từ file idea.txt hoặc chủ đề AI.

Sử dụng:
    python main.py                          # Đọc từ idea.txt (MẶC ĐỊNH)
    python main.py --idea my_script.txt     # Đọc từ file tùy chỉnh
    python main.py --topic "Vũ trụ bí ẩn"  # Sinh tự động bằng Gemini
"""
import argparse
import json
import os
import re
import sys
import time
import unicodedata

from config import OUTPUT_DIR, DEFAULT_NUM_SCENES, VIDEO_WIDTH, VIDEO_HEIGHT, IDEA_FILE
from pipeline.idea_parser import parse_idea_file
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
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text or "video"


def print_banner():
    """In banner đẹp khi khởi chạy."""
    banner = """
╔══════════════════════════════════════════════════╗
║  🎬  AI Video Generation Pipeline  v2.1         ║
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
Chế độ sử dụng:
  python main.py                          # Đọc từ idea.txt (mặc định)
  python main.py --idea script.txt        # Đọc từ file tùy chỉnh
  python main.py --topic "Vũ trụ bí ẩn"  # Sinh bằng Gemini AI
  python main.py --topic "Test" --scenes 3
        """
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Chủ đề video — kích hoạt chế độ Gemini AI"
    )
    parser.add_argument(
        "--idea",
        type=str,
        default=None,
        help=f"Đường dẫn file ý tưởng (mặc định: {IDEA_FILE})"
    )
    parser.add_argument(
        "--scenes",
        type=int,
        default=DEFAULT_NUM_SCENES,
        help=f"Số lượng cảnh cho chế độ Gemini (mặc định: {DEFAULT_NUM_SCENES})"
    )

    args = parser.parse_args()

    print_banner()

    # ═══════════════════════════════════════════════════════════
    # QUYẾT ĐỊNH CHẾ ĐỘ: idea.txt hay Gemini?
    # ═══════════════════════════════════════════════════════════
    use_idea_file = False
    idea_path = None

    if args.topic:
        # Chế độ Gemini — người dùng truyền --topic
        use_idea_file = False
        print("📌 Chế độ: Gemini AI (sinh kịch bản tự động)")
    elif args.idea:
        # Chế độ idea.txt — người dùng chỉ định file cụ thể
        use_idea_file = True
        idea_path = args.idea
        if not os.path.isabs(idea_path):
            idea_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), idea_path)
        print(f"📌 Chế độ: Đọc kịch bản từ file → {idea_path}")
    elif os.path.exists(IDEA_FILE):
        # Mặc định: tìm idea.txt trong thư mục dự án
        use_idea_file = True
        idea_path = IDEA_FILE
        print(f"📌 Chế độ: Đọc kịch bản từ idea.txt (mặc định)")
    else:
        # Không có gì → hỏi topic
        topic = input("📝 Nhập chủ đề video (hoặc tạo file idea.txt): ").strip()
        if not topic:
            print("❌ Không có chủ đề và không tìm thấy file idea.txt!")
            sys.exit(1)
        args.topic = topic
        use_idea_file = False
        print("📌 Chế độ: Gemini AI (sinh kịch bản tự động)")

    print()

    start_time = time.time()

    # ═══════════════════════════════════════════════════════════
    # STEP 1: Lấy kịch bản (từ idea.txt HOẶC Gemini)
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)

    if use_idea_file:
        print("📖 STEP 1/8: Đọc kịch bản từ file idea.txt...")
        print("━" * 50)
        story = parse_idea_file(idea_path)
    else:
        print("📖 STEP 1/8: Sinh kịch bản bằng Gemini AI...")
        print("━" * 50)
        story = generate_story(args.topic, args.scenes)

    # Tạo thư mục output
    slug = slugify(story["title"])
    output_dir = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(output_dir, exist_ok=True)

    # Lưu story.json
    story_path = os.path.join(output_dir, "story.json")
    with open(story_path, 'w', encoding='utf-8') as f:
        json.dump(story, f, ensure_ascii=False, indent=2)

    num_scenes = len(story["scenes"])

    print(f"   📁 Thư mục output: {output_dir}")
    print(f"   📝 Tiêu đề: {story['title']}")
    print(f"   🎬 Số cảnh: {num_scenes}")
    print(f"   📱 Tỷ lệ: 9:16 ({VIDEO_WIDTH}×{VIDEO_HEIGHT})")
    print(f"   ✅ Đã lưu: story.json")
    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 2: Tạo giọng đọc + tính thời lượng
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🎙️  STEP 2/8: Tạo giọng đọc (edge-tts)...")
    print("━" * 50)

    for scene in story["scenes"]:
        sid = scene["scene_id"]
        audio_path = os.path.join(output_dir, f"scene_{sid}.mp3")

        print(f"   🎙️  Scene {sid}: \"{scene['narration'][:50]}...\"")
        generate_voice(scene["narration"], audio_path)

        # Tính duration thực tế từ audio
        duration = get_audio_duration(audio_path)
        scene["actual_duration"] = duration
        print(f"   ✅ scene_{sid}.mp3 ({duration}s)")

    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 3: Tạo Intro/Outro Title Cards
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("🎨 STEP 3/8: Tạo Intro & Outro title cards bằng AI...")
    print("━" * 50)

    intro_image_path = os.path.join(output_dir, "scene_intro.png")
    outro_image_path = os.path.join(output_dir, "scene_outro.png")

    intro_prompt = story.get("intro_prompt")
    outro_prompt = story.get("outro_prompt")

    if intro_prompt:
        print(f"   🖼️  Sinh ảnh nền Intro: \"{intro_prompt[:60]}...\"")
        generate_image(intro_prompt, intro_image_path)
    
    if outro_prompt:
        print(f"   🖼️  Sinh ảnh nền Outro: \"{outro_prompt[:60]}...\"")
        generate_image(outro_prompt, outro_image_path)

    create_intro_card(story["title"], intro_image_path, bg_image_path=intro_image_path)
    create_outro_card(outro_image_path, bg_image_path=outro_image_path)

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
        # Không burn trực tiếp lên ảnh tĩnh để tránh bị phóng to/méo hình khi zoom
        print(f"      📝 Đã lưu ảnh sạch, phụ đề sẽ được vẽ tĩnh trực tiếp lên video: \"{scene['subtitle']}\"")

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
            scene["camera_motion"],
            subtitle_text=scene["subtitle"]
        )
        print(f"   ✅ scene_{sid}.mp4")

    print()

    # ═══════════════════════════════════════════════════════════
    # STEP 6: Tạo phụ đề
    # ═══════════════════════════════════════════════════════════
    print("━" * 50)
    print("📝 STEP 6/8: Tạo phụ đề SRT...")
    print("━" * 50)

    all_scenes_for_srt = []

    all_scenes_for_srt.append({
        "scene_id": "intro",
        "subtitle": "",
        "actual_duration": intro_duration
    })

    for scene in story["scenes"]:
        all_scenes_for_srt.append(scene)

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
    print("🔗 STEP 8/8: Ghép video hoàn chỉnh (fade + nhạc nền + stereo)...")
    print("━" * 50)

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
    mode_label = "📄 idea.txt" if use_idea_file else "🤖 Gemini AI"

    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  ✅  HOÀN THÀNH! — Video 9:16 Premium           ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"   📁 Video: {final_path}")
    print(f"   📱 Tỷ lệ: 9:16 ({VIDEO_WIDTH}×{VIDEO_HEIGHT})")
    print(f"   🎬 Số cảnh: {num_scenes}")
    print(f"   📊 Dung lượng: {file_size_mb:.1f} MB")
    print(f"   ⏱️  Thời gian: {minutes}m {seconds}s")
    print(f"   📌 Nguồn kịch bản: {mode_label}")
    print(f"   💰 Chi phí: $0")
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

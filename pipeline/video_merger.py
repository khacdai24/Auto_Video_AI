"""
Step 7: Ghép tất cả video scenes, audio, và phụ đề bằng FFmpeg.
Bao gồm: fade transitions và audio giọng đọc.
Input: Các file scene_X.mp4, scene_X.mp3, subtitles.srt
Output: final.mp4
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    SUBTITLE_STYLE, FADE_DURATION, 
    AUDIO_SAMPLE_RATE, AUDIO_BITRATE
)


def merge_videos(scenes, output_dir, final_path):
    """
    Ghép tất cả scene videos + audio giọng đọc + phụ đề thành video hoàn chỉnh.

    Pipeline:
    1. Ghép scene videos với fade transitions
    2. Ghép scene audios
    3. Merge video + voice audio
    4. Burn phụ đề → final.mp4

    Args:
        scenes: list of dict (danh sách scenes)
        output_dir: Thư mục chứa các file scene
        final_path: Đường dẫn file output cuối cùng
    """
    scene_videos = []
    scene_audios = []
    for scene in scenes:
        sid = scene["scene_id"]
        scene_videos.append(os.path.join(output_dir, f"scene_{sid}.mp4"))
        scene_audios.append(os.path.join(output_dir, f"scene_{sid}.mp3"))

    # File tạm
    merged_video = os.path.join(output_dir, "_merged_video.mp4")
    merged_audio = os.path.join(output_dir, "_merged_audio.mp3")
    with_audio = os.path.join(output_dir, "_with_audio.mp4")
    srt_path = os.path.join(output_dir, "subtitles.srt")

    try:
        # ═══════════════════════════════════════════
        # Bước 1: Ghép scene videos với FADE TRANSITIONS
        # ═══════════════════════════════════════════
        print("   🔗 Ghép scene videos với fade transitions...")
        _concat_videos_with_fade(scene_videos, scenes, merged_video)

        # ═══════════════════════════════════════════
        # Bước 2: Ghép scene audios
        # ═══════════════════════════════════════════
        print("   🔗 Ghép scene audios...")
        _concat_audios(scene_audios, output_dir, merged_audio)

        # ═══════════════════════════════════════════
        # Bước 3: Merge video + voice audio
        # ═══════════════════════════════════════════
        print("   🎵 Ghép giọng đọc vào video...")
        _run_ffmpeg([
            'ffmpeg', '-y',
            '-i', merged_video,
            '-i', merged_audio,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', AUDIO_BITRATE,
            '-ar', str(AUDIO_SAMPLE_RATE),
            '-ac', '2',             # Stereo
            '-shortest',
            with_audio
        ])

        # ═══════════════════════════════════════════
        # Bước 4: Burn phụ đề
        # ═══════════════════════════════════════════
        if os.path.exists(srt_path):
            print("   📝 Ghi phụ đề vào video...")
            srt_relative = "subtitles.srt"
            try:
                _run_ffmpeg([
                    'ffmpeg', '-y',
                    '-i', with_audio,
                    '-vf', f"subtitles={srt_relative}:force_style='{SUBTITLE_STYLE}'",
                    '-c:a', 'copy',
                    final_path
                ], cwd=output_dir)
            except SystemExit:
                print("   ⚠️ LƯU Ý: FFmpeg trên máy không hỗ trợ bộ lọc 'subtitles' (thiếu libass).")
                print("   👉 Phụ đề đã được burn trực tiếp vào hình ảnh bằng Pillow (fallback).")
                import shutil
                shutil.copy2(with_audio, final_path)
        else:
            print("   ⚠️ Không tìm thấy file phụ đề, bỏ qua...")
            os.rename(with_audio, final_path)
            with_audio = None

    finally:
        # Dọn dẹp file tạm
        temp_files = [merged_video, merged_audio, with_audio]
        for f in temp_files:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        # Xóa file list tạm
        for tmp in ["_video_list.txt", "_audio_list.txt"]:
            tmp_path = os.path.join(output_dir, tmp)
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def _concat_videos_with_fade(scene_videos, scenes, output_path):
    """Ghép scene videos với hiệu ứng fade transition giữa các cảnh."""
    if len(scene_videos) == 1:
        # Chỉ 1 scene — copy trực tiếp
        import shutil
        shutil.copy2(scene_videos[0], output_path)
        return

    fade_dur = FADE_DURATION
    n = len(scene_videos)

    # Xây dựng FFmpeg filter_complex cho xfade
    inputs = []
    for v in scene_videos:
        inputs.extend(['-i', v])

    # Tính offset cho mỗi xfade
    # offset = tổng duration các scene trước - tổng fade duration trước
    offsets = []
    cumulative = 0
    for i in range(n - 1):
        dur = scenes[i].get("actual_duration", 8.0)
        cumulative += dur
        offset = cumulative - fade_dur * (i + 1)
        offsets.append(max(0, offset))

    # Xây filter chain
    filter_parts = []
    current_input = "[0:v]"

    for i in range(n - 1):
        next_input = f"[{i + 1}:v]"
        out_label = f"[v{i}]" if i < n - 2 else "[vout]"
        filter_parts.append(
            f"{current_input}{next_input}xfade=transition=fade:duration={fade_dur}:offset={offsets[i]}{out_label}"
        )
        current_input = out_label

    filter_complex = ";".join(filter_parts)

    cmd = ['ffmpeg', '-y'] + inputs + [
        '-filter_complex', filter_complex,
        '-map', '[vout]',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        output_path
    ]

    try:
        _run_ffmpeg(cmd)
    except SystemExit:
        # Fallback: concat đơn giản nếu xfade thất bại
        print("   ⚠️ xfade thất bại, dùng concat đơn giản...")
        _concat_videos_simple(scene_videos, output_path)


def _concat_videos_simple(scene_videos, output_path):
    """Concat videos đơn giản bằng concat demuxer (fallback)."""
    output_dir = os.path.dirname(output_path)
    video_list = os.path.join(output_dir, "_video_list.txt")

    with open(video_list, 'w') as f:
        for v in scene_videos:
            f.write(f"file '{v}'\n")

    _run_ffmpeg([
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', video_list,
        '-c', 'copy',
        output_path
    ])


def _concat_audios(scene_audios, output_dir, output_path):
    """Ghép scene audios bằng concat."""
    audio_list = os.path.join(output_dir, "_audio_list.txt")

    with open(audio_list, 'w') as f:
        for a in scene_audios:
            f.write(f"file '{a}'\n")

    _run_ffmpeg([
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0',
        '-i', audio_list,
        '-c:a', 'libmp3lame',
        '-ar', str(AUDIO_SAMPLE_RATE),
        output_path
    ])


def _run_ffmpeg(cmd, cwd=None):
    """Chạy lệnh FFmpeg với error handling."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi FFmpeg:")
        # In 500 ký tự cuối cùng của stderr
        stderr = e.stderr if e.stderr else ""
        print(f"   {stderr[-500:]}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ FFmpeg chưa được cài đặt!")
        print("   👉 Cài bằng Homebrew: brew install ffmpeg")
        sys.exit(1)

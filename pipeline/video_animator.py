"""
Step 5: Chuyển ảnh thành video bằng FFmpeg Ken Burns Effect.
Input: File ảnh .png + camera_motion + duration
Output: File video .mp4

Chỉ hỗ trợ zoom_in và zoom_out — mượt mà, không rung lắc.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VIDEO_FPS, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_BITRATE


def _zoom_value(camera_motion, frame_index, total_frames):
    """Tính zoom theo frame, dùng easing nhẹ để chuyển động đều và ít gắt."""
    progress = frame_index / max(total_frames - 1, 1)
    eased = progress * progress * (3 - 2 * progress)

    if camera_motion == "zoom_out":
        return 1.18 - 0.18 * eased
    return 1.0 + 0.18 * eased


def _resize_cover(img, width, height):
    """Resize ảnh để phủ kín khung dọc, sau đó crop chính giữa."""
    src_w, src_h = img.size
    scale = max(width / src_w, height / src_h)
    resized_w = int(round(src_w * scale))
    resized_h = int(round(src_h * scale))

    resized = img.resize((resized_w, resized_h), resample=_resampling_lanczos())
    left = (resized_w - width) // 2
    top = (resized_h - height) // 2
    return resized.crop((left, top, left + width, top + height))


def _render_zoom_frames(image_path, process, total_frames, camera_motion):
    """Render từng frame bằng Pillow rồi pipe raw RGB vào FFmpeg."""
    from PIL import Image

    base = Image.open(image_path).convert("RGB")
    base = _resize_cover(base, VIDEO_WIDTH, VIDEO_HEIGHT)

    for frame_index in range(total_frames):
        zoom = _zoom_value(camera_motion, frame_index, total_frames)
        zoom_w = int(round(VIDEO_WIDTH * zoom))
        zoom_h = int(round(VIDEO_HEIGHT * zoom))

        frame = base.resize((zoom_w, zoom_h), resample=_resampling_lanczos())
        left = (zoom_w - VIDEO_WIDTH) // 2
        top = (zoom_h - VIDEO_HEIGHT) // 2
        frame = frame.crop((left, top, left + VIDEO_WIDTH, top + VIDEO_HEIGHT))
        process.stdin.write(frame.tobytes())


def _resampling_lanczos():
    """Tương thích Pillow cũ/mới cho resampling chất lượng cao."""
    from PIL import Image

    try:
        return Image.Resampling.LANCZOS
    except AttributeError:
        return Image.LANCZOS


def animate_image(image_path, output_path, duration, camera_motion="zoom_in"):
    """
    Tạo video từ ảnh tĩnh với hiệu ứng Ken Burns (zoom only, mượt mà).

    Args:
        image_path: Đường dẫn file ảnh (.png)
        output_path: Đường dẫn file video output (.mp4)
        duration: Thời lượng video (giây)
        camera_motion: Loại hiệu ứng (zoom_in hoặc zoom_out)
    """
    # Kiểm tra FFmpeg
    _check_ffmpeg()

    total_frames = int(duration * VIDEO_FPS)
    if total_frames < 1:
        total_frames = VIDEO_FPS  # Tối thiểu 1 giây

    cmd = [
        'ffmpeg',
        '-y',                          # Ghi đè file nếu tồn tại
        '-hide_banner',
        '-loglevel', 'error',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-s', f'{VIDEO_WIDTH}x{VIDEO_HEIGHT}',
        '-r', str(VIDEO_FPS),
        '-i', '-',
        '-c:v', 'libx264',            # Codec H.264
        '-b:v', VIDEO_BITRATE,        # Bitrate cao (3Mbps)
        '-preset', 'slow',            # Chất lượng encode cao hơn
        '-r', str(VIDEO_FPS),
        '-pix_fmt', 'yuv420p',         # Pixel format tương thích
        output_path
    ]

    process = None
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _render_zoom_frames(image_path, process, total_frames, camera_motion)
        _, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                cmd,
                stderr=stderr.decode("utf-8", errors="replace")
            )
    except (BrokenPipeError, subprocess.CalledProcessError) as e:
        print(f"❌ Lỗi FFmpeg khi tạo video:")
        stderr = getattr(e, "stderr", "") or ""
        print(f"   {stderr[-500:]}")  # In 500 ký tự cuối của lỗi
        sys.exit(1)
    finally:
        if process and process.stdin and not process.stdin.closed:
            process.stdin.close()


def _check_ffmpeg():
    """Kiểm tra FFmpeg đã được cài đặt chưa."""
    try:
        subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            check=True
        )
    except FileNotFoundError:
        print("❌ FFmpeg chưa được cài đặt!")
        print("   👉 Cài bằng Homebrew: brew install ffmpeg")
        sys.exit(1)

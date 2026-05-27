"""
Step 2: Tạo giọng đọc bằng edge-tts (miễn phí).
Input: Văn bản narration
Output: File .mp3
"""
import asyncio
import sys

import edge_tts

sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from config import TTS_VOICE, TTS_RATE


async def _generate_voice_async(text, output_path, voice=None, rate=None):
    """Tạo file audio từ text bằng edge-tts (async)."""
    voice = voice or TTS_VOICE
    rate = rate or TTS_RATE

    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_voice(text, output_path, voice=None, rate=None):
    """
    Tạo file audio từ text bằng edge-tts.
    Chạy trong một subprocess để tránh xung đột SSL/LibreSSL trên Python 3.9 macOS
    khi import thư viện Google trước đó.
    Tích hợp retry logic và delay để tránh rate-limit từ Microsoft server.

    Args:
        text: Văn bản cần đọc (tiếng Việt)
        output_path: Đường dẫn file output (.mp3)
        voice: Giọng đọc (mặc định từ config)
        rate: Tốc độ đọc (mặc định từ config)
    """
    import subprocess
    import time
    voice = voice or TTS_VOICE
    rate = rate or TTS_RATE

    # Đoạn code Python chạy độc lập trong tiến trình mới
    script = f"""
import asyncio
import sys
import edge_tts

async def run():
    try:
        communicate = edge_tts.Communicate({repr(text)}, {repr(voice)}, rate={repr(rate)})
        await communicate.save({repr(output_path)})
    except Exception as e:
        print(f"ERROR: {{e}}", file=sys.stderr)
        sys.exit(1)

asyncio.run(run())
"""

    # Tạo env sạch cho subprocess — tắt gRPC fork support để tránh lỗi
    import os
    clean_env = os.environ.copy()
    clean_env["GRPC_ENABLE_FORK_SUPPORT"] = "0"
    clean_env["GRPC_POLL_STRATEGY"] = "epoll1"

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            # Nghỉ một chút trước mỗi lần gọi (tránh rate limit khi gọi liên tiếp nhiều scene)
            if attempt > 1:
                wait_time = attempt * 5
                print(f"   ⏳ Tạm dừng {wait_time}s trước khi thử lại tạo giọng đọc...")
                time.sleep(wait_time)
            elif "scene_1.mp3" not in output_path:
                # Tạm dừng nhẹ giữa các scene
                time.sleep(3.0)

            subprocess.run(
                [sys.executable, "-c", script],
                capture_output=True,
                text=True,
                check=True,
                env=clean_env
            )
            # Thành công -> thoát vòng lặp
            break
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() or e.stdout.strip()
            print(f"   ⚠️ Lần thử {attempt}/{max_retries} thất bại: {error_msg}")
            if attempt == max_retries:
                print("   ⚠️ Edge-TTS bị lỗi liên tục. Kích hoạt fallback gTTS (Google TTS)...")
                try:
                    from gtts import gTTS
                    tts = gTTS(text=text, lang='vi', slow=False)
                    tts.save(output_path)
                    print("   ✅ Đã tạo giọng đọc bằng gTTS (fallback) thành công!")
                except Exception as gtts_e:
                    print(f"❌ Lỗi cả Edge-TTS và gTTS: {gtts_e}")
                    sys.exit(1)


def list_vietnamese_voices():
    """Liệt kê các giọng đọc tiếng Việt có sẵn."""
    async def _list():
        voices = await edge_tts.list_voices()
        vn_voices = [v for v in voices if v["Locale"].startswith("vi-")]
        return vn_voices

    voices = asyncio.run(_list())
    print("\n🎙️ Giọng đọc tiếng Việt có sẵn:")
    for v in voices:
        gender = "👩" if v["Gender"] == "Female" else "👨"
        friendly_name = v.get("FriendlyName", v["ShortName"])
        print(f"   {gender} {v['ShortName']} — {friendly_name}")
    return voices

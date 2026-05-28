"""
Cấu hình cho AI Video Generation Pipeline.
Chỉnh sửa các giá trị bên dưới theo nhu cầu.
"""
import os

# ============================================================
# 📄 File ý tưởng kịch bản (idea.txt)
# Nếu có file này, pipeline sẽ đọc kịch bản từ đây thay vì gọi Gemini
# ============================================================
IDEA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "idea.txt")

# ============================================================
# 🔑 GEMINI API KEY (Miễn phí)
# Lấy tại: https://aistudio.google.com/apikey
# ============================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCk790qBoCxspBarbteErT9u_mA_xamiQ8")
GEMINI_MODEL = "gemini-1.5-flash"
# Danh sách model dự phòng (thử lần lượt nếu model chính bị quota)
GEMINI_FALLBACK_MODELS = [
    "gemini-1.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
]

# ============================================================
# 🎙️ Cấu hình giọng đọc (edge-tts)
# ============================================================
TTS_VOICE = "vi-VN-NamMinhNeural"  # Giọng nữ tiếng Việt
# Các lựa chọn khác:
#   vi-VN-NamMinhNeural  (nam, tiếng Việt)
#   en-US-JennyNeural    (nữ, tiếng Anh)
#   en-US-GuyNeural      (nam, tiếng Anh)
TTS_RATE = "+15%"  # Tốc độ đọc nhanh hơn một chút

# ============================================================
# 🖼️ Cấu hình sinh ảnh (Pollinations.ai)
# Tỷ lệ dọc 9:16, dư biên cho hiệu ứng zoom
# ============================================================
IMAGE_WIDTH = 768
IMAGE_HEIGHT = 1344
IMAGE_MODEL = "flux-realism"
# Các model khác trên Pollinations.ai:
#   "flux"           — Mặc định, cân bằng tốc độ/chất lượng
#   "flux-pro"       — Chất lượng cao, chi tiết hơn
#   "flux-realism"   — Chuyên ảnh thực tế (realistic)
#   "flux-anime"     — Phong cách anime
#   "flux-3d"        — Phong cách 3D render
#   "turbo"          — Tốc độ nhanh, chất lượng vừa

# ============================================================
# 🎬 Cấu hình video — Tỷ lệ 9:16 (dọc, TikTok/Reels/Shorts)
# ============================================================
VIDEO_FPS = 30
VIDEO_WIDTH = 720
VIDEO_HEIGHT = 1280
VIDEO_BITRATE = "3M"       # 3 Mbps — sắc nét hơn nhiều (trước: ~680kbps)

# ============================================================
# 🔊 Cấu hình audio
# ============================================================
AUDIO_SAMPLE_RATE = 44100  # 44.1kHz stereo chất lượng cao
AUDIO_BITRATE = "128k"     # 128kbps (trước: 63kbps mono)

# ============================================================
# 📝 Cấu hình phụ đề — Burned-in bằng Pillow
# ============================================================
SUBTITLE_FONT_SIZE_RATIO = 0.025  # Gần size cũ: ~32px trên ảnh/video cao 1280px
SUBTITLE_Y_RATIO = 0.40            # Đưa phụ đề lên cao hơn (khu vực an toàn), tránh bị giao diện MXH che khuất

# Giữ lại SUBTITLE_STYLE cho fallback FFmpeg subtitles filter
SUBTITLE_STYLE = (
    "FontSize=28,"
    "FontName=Arial,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "BackColour=&H80000000,"
    "Outline=2,"
    "Shadow=1,"
    "MarginV=50"
)

# ============================================================
# 🎞️ Cấu hình chuyển cảnh
# ============================================================
FADE_DURATION = 0.5  # 0.5s fade giữa các scene

# ============================================================
# 📁 Đường dẫn
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# ============================================================
# 🔢 Mặc định
# ============================================================
DEFAULT_NUM_SCENES = 5

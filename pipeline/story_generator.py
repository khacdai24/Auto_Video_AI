import json
import sys
import time

import google.generativeai as genai

# Import config từ thư mục cha
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))))
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FALLBACK_MODELS


def generate_story(topic, num_scenes=5):
    """
    Sinh kịch bản video từ chủ đề bằng Gemini API Free.
    Tự động thử nhiều model nếu model chính bị quota.

    Args:
        topic: Chủ đề video (tiếng Việt hoặc tiếng Anh)
        num_scenes: Số lượng cảnh

    Returns:
        dict: Kịch bản có cấu trúc {"title": ..., "scenes": [...]}
    """
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE" or not GEMINI_API_KEY:
        print("❌ Lỗi: Chưa cấu hình GEMINI_API_KEY!")
        print("   👉 Lấy API key miễn phí tại: https://aistudio.google.com/apikey")
        print("   👉 Sau đó sửa file config.py hoặc đặt biến môi trường:")
        print('      export GEMINI_API_KEY="your_key_here"')
        sys.exit(1)

    genai.configure(api_key=GEMINI_API_KEY)

    prompt = _build_prompt(topic, num_scenes)

    # Thử model chính trước, sau đó fallback
    models_to_try = [GEMINI_MODEL] + [m for m in GEMINI_FALLBACK_MODELS if m != GEMINI_MODEL]

    for model_name in models_to_try:
        try:
            text = _call_gemini(model_name, prompt)
            if text:
                story = _parse_and_validate(text)
                if story:
                    return story
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print(f"   ⚠️  Model '{model_name}' hết quota, thử model khác...")
                continue
            elif "not found" in error_msg.lower() or "404" in error_msg:
                print(f"   ⚠️  Model '{model_name}' không tồn tại, thử model khác...")
                continue
            else:
                print(f"   ⚠️  Lỗi với model '{model_name}': {error_msg[:200]}")
                continue

    print("❌ Tất cả model đều thất bại!")
    print("   Có thể API key đã hết quota hôm nay.")
    print("   👉 Thử lại sau hoặc tạo API key mới tại: https://aistudio.google.com/apikey")
    sys.exit(1)


def _call_gemini(model_name, prompt, max_retries=2):
    """Gọi Gemini API với retry logic."""
    model = genai.GenerativeModel(model_name)

    for attempt in range(1, max_retries + 1):
        try:
            print(f"   📡 Đang gọi Gemini API ({model_name})...")
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            # Nếu quota = 0 (model không khả dụng), raise ngay
            if "limit: 0" in error_msg:
                raise
            # Nếu rate limit tạm thời, chờ rồi thử lại
            if ("retry" in error_msg.lower() or "429" in error_msg) and attempt < max_retries:
                wait = 35  # Chờ 35s theo khuyến nghị
                print(f"   ⏳ Rate limit, chờ {wait}s rồi thử lại...")
                time.sleep(wait)
                continue
            raise

    return None


def _build_prompt(topic, num_scenes):
    """Tạo prompt cho Gemini."""
    return f"""Bạn là một người viết kịch bản video ngắn chuyên nghiệp cho TikTok/YouTube Shorts.

Hãy viết kịch bản cho một video ngắn DỌC (tỷ lệ 9:16) về chủ đề: "{topic}"

Yêu cầu:
- Video gồm {num_scenes} cảnh
- Mỗi cảnh có lời thoại (narration) khoảng 2-3 câu, tự nhiên, dễ nghe, nhịp nhanh cuốn hút
- Nội dung hấp dẫn, cuốn hút, phù hợp nền tảng video ngắn

Trả về ĐÚNG JSON format như sau (KHÔNG markdown, KHÔNG giải thích thêm):

{{
  "title": "Tiêu đề video bằng tiếng Việt",
  "intro_prompt": "English visual prompt for intro title card, cinematic theme related background, no text, clean copy space, 9:16 vertical composition",
  "outro_prompt": "English visual prompt for outro card, cinematic theme related background, no text, clean copy space, 9:16 vertical composition",
  "scenes": [
    {{
      "scene_id": 1,
      "narration": "Lời thoại tiếng Việt cho cảnh này. Viết tự nhiên, hấp dẫn.",
      "visual_prompt": "Detailed English description for AI image generation in PORTRAIT/VERTICAL composition (9:16 aspect ratio). Include art style, lighting, mood. Example: cinematic portrait shot of a futuristic city at sunset, vertical composition, towering neon-lit skyscrapers, wet streets below, highly detailed, 4k",
      "camera_motion": "zoom_in",
      "subtitle": "Phụ đề tóm tắt lời thoại siêu ngắn gọn (dưới 8 từ) bằng tiếng Việt"
    }}
  ]
}}

Quy tắc BẮT BUỘC:
1. narration và subtitle PHẢI bằng tiếng Việt. Phụ đề (subtitle) PHẢI là câu tóm tắt cực kỳ ngắn gọn, súc tích (dưới 8 từ) mô tả ý chính của lời thoại để người xem đọc nhanh trên điện thoại.
2. visual_prompt, intro_prompt, và outro_prompt PHẢI bằng tiếng Anh (cho AI sinh ảnh), PHẢI mô tả theo bố cục DỌC (portrait, vertical composition, 9:16). Ví dụ: close-up shot, portrait framing, vertical composition, towering elements, no text, copy space.
3. camera_motion CHỈ chọn 1 trong 2: zoom_in hoặc zoom_out. TUYỆT ĐỐI KHÔNG dùng pan_left, pan_right
4. Xen kẽ zoom_in và zoom_out giữa các cảnh
5. CHỈ trả về JSON thuần túy, tuyệt đối không có markdown hoặc text khác"""


def _parse_and_validate(text):
    """Parse JSON và validate cấu trúc story."""
    text = _clean_json_response(text)

    try:
        story = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"   ⚠️  Lỗi parse JSON: {e}")
        print(f"   Response gốc:\n{text[:300]}")
        return None

    # Validate cấu trúc
    if "title" not in story or "scenes" not in story:
        print("   ⚠️  JSON không có 'title' hoặc 'scenes'")
        return None

    # Fallback/default cho intro_prompt và outro_prompt
    if "intro_prompt" not in story and story["scenes"]:
        story["intro_prompt"] = story["scenes"][0]["visual_prompt"] + ", clean title card background, no text, copy space"
    if "outro_prompt" not in story and story["scenes"]:
        story["outro_prompt"] = story["scenes"][-1]["visual_prompt"] + ", clean closing card background, no text, copy space"

    required_fields = ["scene_id", "narration", "visual_prompt", "camera_motion", "subtitle"]
    for scene in story["scenes"]:
        for field in required_fields:
            if field not in scene:
                print(f"   ⚠️  Scene {scene.get('scene_id', '?')} thiếu field '{field}'")
                return None

        # Validate camera_motion — chỉ cho phép zoom_in/zoom_out
        valid_motions = ["zoom_in", "zoom_out"]
        if scene["camera_motion"] not in valid_motions:
            scene["camera_motion"] = "zoom_in"  # Fallback

    return story


def _clean_json_response(text):
    """Loại bỏ markdown code block và text thừa từ response."""
    # Loại bỏ ```json ... ``` hoặc ``` ... ```
    if text.startswith("```"):
        # Bỏ dòng đầu (```json hoặc ```)
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # Bỏ ``` cuối
        last_backtick = text.rfind("```")
        if last_backtick != -1:
            text = text[:last_backtick]

    text = text.strip()

    # Tìm JSON object trong text (từ { đầu tiên đến } cuối cùng)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text

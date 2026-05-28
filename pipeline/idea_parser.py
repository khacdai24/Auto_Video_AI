"""
Parser file idea.txt → story dict.

Format idea.txt:
    # VIDEO: Tiêu đề video

    ## Thời gian: 00:00 - 00:04
    Lời thoại (Voiceover):
    "Lời thoại tiếng Việt..."

    Gợi ý hình ảnh cho AI (Visual Prompt):
    English image prompt here...

    Camera: zoom_in

    ---

Quy tắc:
- Dòng `# VIDEO:` → tiêu đề
- Mỗi block `## Thời gian:` ... `---` → 1 scene
- `Camera:` là TÙY CHỌN (mặc định xen kẽ zoom_in/zoom_out)
- Lời thoại có thể có hoặc không có dấu ngoặc kép
"""
import os
import re
import sys


def parse_idea_file(filepath):
    """
    Parse file idea.txt thành story dict giống output Gemini.

    Args:
        filepath: Đường dẫn tới file idea.txt

    Returns:
        dict: {"title": "...", "scenes": [...]}

    Raises:
        FileNotFoundError: Nếu file không tồn tại
        ValueError: Nếu file không đúng format
    """
    if not os.path.exists(filepath):
        print(f"❌ Không tìm thấy file: {filepath}")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # ═══════════════════════════════════════
    # Parse tiêu đề
    # ═══════════════════════════════════════
    title_match = re.search(r'^#\s*VIDEO:\s*(.+)$', content, re.MULTILINE)
    if not title_match:
        print("❌ File idea.txt thiếu dòng tiêu đề!")
        print("   👉 Dòng đầu tiên phải là: # VIDEO: Tiêu đề video")
        sys.exit(1)

    title = title_match.group(1).strip()

    # ═══════════════════════════════════════
    # Parse Intro / Outro prompts (tùy chọn)
    # ═══════════════════════════════════════
    intro_match = re.search(r'^#\s*(?:INTRO\s*PROMPT|INTRO\s*VISUAL|INTRO):\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
    outro_match = re.search(r'^#\s*(?:OUTRO\s*PROMPT|OUTRO\s*VISUAL|OUTRO):\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)

    intro_prompt = intro_match.group(1).strip() if intro_match else None
    outro_prompt = outro_match.group(1).strip() if outro_match else None

    # ═══════════════════════════════════════
    # Tách các scene blocks bằng `---`
    # ═══════════════════════════════════════
    # Bỏ phần trước scene đầu tiên (tiêu đề)
    # Tìm tất cả blocks bắt đầu bằng ## Thời gian:
    scene_blocks = re.split(r'\n---\s*\n', content)

    scenes = []
    scene_id = 0

    for block in scene_blocks:
        block = block.strip()
        if not block:
            continue

        # Kiểm tra block này có phải scene không (có ## Thời gian:)
        time_match = re.search(
            r'##\s*Thời gian:\s*(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})',
            block
        )
        if not time_match:
            continue

        scene_id += 1
        time_start = time_match.group(1)
        time_end = time_match.group(2)

        # ═══════════════════════════════════════
        # Parse lời thoại
        # ═══════════════════════════════════════
        narration = _extract_narration(block)
        if not narration:
            print(f"   ⚠️ Scene {scene_id}: Không tìm thấy lời thoại, bỏ qua.")
            continue

        # ═══════════════════════════════════════
        # Parse visual prompt
        # ═══════════════════════════════════════
        visual_prompt = _extract_visual_prompt(block)
        if not visual_prompt:
            print(f"   ⚠️ Scene {scene_id}: Không tìm thấy visual prompt, bỏ qua.")
            continue

        # ═══════════════════════════════════════
        # Parse camera motion (tùy chọn)
        # ═══════════════════════════════════════
        camera_motion = _extract_camera(block, scene_id)

        # ═══════════════════════════════════════
        # Parse phụ đề (nếu có trong file, ngược lại tự động tạo bằng Gemini/fallback)
        # ═══════════════════════════════════════
        subtitle = _extract_subtitle(block)

        scenes.append({
            "scene_id": scene_id,
            "narration": narration,
            "visual_prompt": visual_prompt,
            "camera_motion": camera_motion,
            "subtitle": subtitle,
            "time_start": time_start,
            "time_end": time_end,
        })

    if not scenes:
        print("❌ File idea.txt không chứa scene nào hợp lệ!")
        print("   👉 Mỗi scene cần có: ## Thời gian:, Lời thoại, Visual Prompt")
        sys.exit(1)

    # Tự động tóm tắt phụ đề bằng Gemini nếu thiếu
    scenes_to_summarize = [s for s in scenes if not s["subtitle"]]
    if scenes_to_summarize:
        print(f"   📡 Đang tóm tắt {len(scenes_to_summarize)} phụ đề thiếu bằng Gemini...")
        narrations = [s["narration"] for s in scenes_to_summarize]
        summarized_subs = batch_summarize_narrations(narrations)
        for scene, sub in zip(scenes_to_summarize, summarized_subs):
            scene["subtitle"] = sub
            print(f"      📝 Scene {scene['scene_id']}: \"{scene['subtitle']}\"")

    # Gán fallback cho intro_prompt và outro_prompt nếu chưa có
    if not intro_prompt and scenes:
        first_prompt = scenes[0]["visual_prompt"]
        intro_prompt = f"{first_prompt}, clean title card background, no text, copy space"

    if not outro_prompt and scenes:
        last_prompt = scenes[-1]["visual_prompt"]
        outro_prompt = f"{last_prompt}, clean closing card background, no text, copy space"

    print(f"   ✅ Tiêu đề: {title}")
    print(f"   ✅ Số cảnh: {len(scenes)}")

    return {
        "title": title,
        "scenes": scenes,
        "intro_prompt": intro_prompt,
        "outro_prompt": outro_prompt
    }


def _extract_narration(block):
    """Trích xuất lời thoại từ block scene."""
    match = re.search(
        r'Lời thoại\s*\(Voiceover\)\s*:\s*\n(.+?)(?=\n\s*(?:Phụ đề|Subtitle|Gợi ý hình ảnh|Visual Prompt|Camera:|---)|\.?\Z)',
        block,
        re.DOTALL | re.IGNORECASE
    )
    if not match:
        # Fallback: tìm dòng có dấu ngoặc kép
        match = re.search(r'["\u201c\u201d](.+?)["\u201c\u201d]', block, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    text = match.group(1).strip()
    text = text.strip('"\u201c\u201d\u2018\u2019')
    return text.strip()


def _extract_subtitle(block):
    """Trích xuất phụ đề tùy chỉnh từ block scene (nếu có)."""
    match = re.search(
        r'(?:Phụ đề|Subtitle)[^:]*:\s*\n(.+?)(?=\n\s*(?:Lời thoại|Voiceover|Gợi ý hình ảnh|Visual Prompt|Camera:|---)|\.?\Z)',
        block,
        re.DOTALL | re.IGNORECASE
    )
    if match:
        return match.group(1).strip().strip('"\u201c\u201d\u2018\u2019')
    return None


def _extract_visual_prompt(block):
    """Trích xuất visual prompt từ block scene."""
    match = re.search(
        r'(?:Gợi ý hình ảnh|Visual Prompt)[^:]*:\s*\n(.+?)(?=\n\s*(?:Lời thoại|Voiceover|Phụ đề|Subtitle|Camera:|---)|\.?\Z)',
        block,
        re.DOTALL | re.IGNORECASE
    )
    if not match:
        return None
    return match.group(1).strip()


def _extract_camera(block, scene_id):
    """Trích xuất camera motion. Mặc định xen kẽ zoom_in/zoom_out."""
    match = re.search(r'Camera:\s*(zoom_in|zoom_out)', block, re.IGNORECASE)
    if match:
        return match.group(1).lower()

    # Mặc định: xen kẽ
    return "zoom_in" if scene_id % 2 == 1 else "zoom_out"


def _make_subtitle(narration, max_len=65):
    """Rút gọn lời thoại thành subtitle ngắn gọn."""
    # Lấy câu đầu tiên
    sentences = re.split(r'[.?!…]', narration)
    sentences = [s.strip() for s in sentences if s.strip()]
    first_sentence = sentences[0] if sentences else narration

    if len(first_sentence) <= max_len:
        return first_sentence

    # Cắt ngắn tại ranh giới từ
    truncated = first_sentence[:max_len]
    last_space = truncated.rfind(' ')
    if last_space > max_len // 2:
        truncated = truncated[:last_space]

    return truncated + "..."


def batch_summarize_narrations(narrations):
    """
    Sử dụng Gemini để tóm tắt danh sách lời thoại thành các phụ đề siêu ngắn gọn (< 8 từ) bằng tiếng Việt.
    """
    import google.generativeai as genai
    from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FALLBACK_MODELS
    import json

    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE" or GEMINI_API_KEY == "":
        print("   ⚠️  Không tìm thấy Gemini API Key, sử dụng thuật toán tóm tắt local...")
        return [_local_fallback_summary(n) for n in narrations]

    genai.configure(api_key=GEMINI_API_KEY)

    # Xây dựng prompt
    prompt = """Bạn là chuyên gia viết phụ đề cho video ngắn (TikTok/Reels/Shorts).
Hãy tóm tắt các câu thoại dưới đây thành các phụ đề (subtitle) siêu ngắn, súc tích (dưới 8 từ, tuyệt đối KHÔNG chứa dấu ba chấm "...") bằng tiếng Việt.
Yêu cầu phụ đề phải cô đọng được ý chính hoặc thông điệp cốt lõi của câu thoại để người xem có thể đọc lướt trên điện thoại trong 1-2 giây. Tuyệt đối không dịch nghĩa thô hay chỉ cắt cụt câu.

Danh sách câu thoại cần tóm tắt:
"""
    for i, narration in enumerate(narrations):
        prompt += f"{i+1}. {narration}\n"

    prompt += """
Trả về kết quả dưới dạng một JSON array gồm các chuỗi (string) phụ đề tương ứng, ví dụ:
[
  "Phụ đề tóm tắt 1",
  "Phụ đề tóm tắt 2"
]
Chú ý: Chỉ trả về JSON thuần túy, không có markdown (như ```json) hay giải thích gì thêm."""

    # Thử model chính trước, sau đó fallback
    models_to_try = [GEMINI_MODEL] + [m for m in GEMINI_FALLBACK_MODELS if m != GEMINI_MODEL]

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()

            # Clean JSON response
            if text.startswith("```"):
                first_newline = text.find("\n")
                if first_newline != -1:
                    text = text[first_newline + 1:]
                last_backtick = text.rfind("```")
                if last_backtick != -1:
                    text = text[:last_backtick]
            text = text.strip()
            
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1 and end > start:
                text = text[start:end + 1]

            subtitles = json.loads(text)
            if isinstance(subtitles, list) and len(subtitles) == len(narrations):
                cleaned = [str(s).strip('"\u201c\u201d\u2018\u2019 ') for s in subtitles]
                return cleaned
        except Exception as e:
            print(f"   ⚠️ Lỗi với model '{model_name}': {e}")
            continue

    print("   ⚠️ Tất cả các model tóm tắt đều thất bại, dùng local fallback...")
    return [_local_fallback_summary(n) for n in narrations]


def _local_fallback_summary(narration, max_words=8):
    """
    Tóm tắt local thông minh hơn bằng cách tách các vế câu qua dấu câu (dấu phẩy, hai chấm, chấm phẩy, ba chấm).
    Đảm bảo câu ngắn gọn nhưng có ý nghĩa trọn vẹn, không bị cắt cụt lửng lơ ở cuối từ.
    """
    # Loại bỏ ngoặc kép và khoảng trắng thừa
    text = narration.strip('"\u201c\u201d\u2018\u2019 ')
    
    # Tách câu đầu tiên nếu có nhiều câu
    sentences = re.split(r'[.?!]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    first_sentence = sentences[0] if sentences else text
    
    # Nếu câu đầu tiên ngắn (dưới max_words từ), lấy luôn cả câu
    words = first_sentence.split()
    if len(words) <= max_words:
        return first_sentence
        
    # Tách câu thành các vế bằng các dấu câu phổ biến
    clauses = re.split(r'[,:;…\-\—]', first_sentence)
    clauses = [c.strip() for c in clauses if c.strip()]
    
    # Duyệt qua các vế để tìm vế có độ dài thích hợp nhất (từ 3 đến max_words từ)
    for clause in clauses:
        clause_words = clause.split()
        if 3 <= len(clause_words) <= max_words:
            # Viết hoa chữ cái đầu
            if len(clause) > 1:
                return clause[0].upper() + clause[1:]
            return clause
            
    # Nếu không tìm thấy vế nào phù hợp, lấy vế đầu tiên nếu vế đó dưới 10 từ
    if clauses:
        first_clause = clauses[0]
        clause_words = first_clause.split()
        if len(clause_words) <= 10:
            return first_clause
            
    # Fallback cuối cùng: cắt cúp theo số lượng từ tối đa nhưng không thêm dấu ba chấm
    return " ".join(words[:max_words])

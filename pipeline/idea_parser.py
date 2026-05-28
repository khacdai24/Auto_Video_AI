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
        # Parse phụ đề (nếu có trong file, ngược lại tự động tạo)
        # ═══════════════════════════════════════
        subtitle = _extract_subtitle(block)
        if not subtitle:
            subtitle = _make_subtitle(narration)

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

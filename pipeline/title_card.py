"""
Tạo Intro/Outro Title Card bằng Pillow.
Dùng gradient background đẹp + text đổ bóng cho video chuyên nghiệp.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VIDEO_WIDTH, VIDEO_HEIGHT


def create_intro_card(title, output_path, width=None, height=None):
    """
    Tạo intro title card với gradient background đẹp.
    
    Args:
        title: Tiêu đề video (tiếng Việt)
        output_path: Đường dẫn file output (.png)
        width: Chiều rộng (mặc định từ config)
        height: Chiều cao (mặc định từ config)
    """
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # ═══════════════════════════════════════
    # Gradient background: Deep blue → Purple → Dark
    # ═══════════════════════════════════════
    for y in range(height):
        ratio = y / height
        # Dark blue → Deep purple gradient
        r = int(15 + 40 * ratio)
        g = int(10 + 15 * ratio)
        b = int(60 + 80 * (1 - ratio))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # ═══════════════════════════════════════
    # Decorative elements: Subtle glowing circles
    # ═══════════════════════════════════════
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Vòng tròn trang trí mờ
    circles = [
        (width * 0.2, height * 0.3, 120, (100, 80, 200, 25)),
        (width * 0.8, height * 0.6, 150, (60, 100, 220, 20)),
        (width * 0.5, height * 0.15, 80, (150, 100, 250, 30)),
    ]
    for cx, cy, radius, color in circles:
        overlay_draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=color
        )

    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img)

    # ═══════════════════════════════════════
    # Title text — Lớn, đổ bóng, ở giữa
    # ═══════════════════════════════════════
    # Font size ~ 6% chiều cao (to cho portrait mode)
    title_font_size = int(height * 0.055)
    title_font = _get_font(title_font_size)

    # Wrap title thành các dòng ngắn (max 15 ký tự cho portrait)
    lines = textwrap.wrap(title, width=14)

    # Tính tổng chiều cao text
    line_heights = []
    line_widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])

    total_text_height = sum(line_heights) + 12 * (len(lines) - 1)
    start_y = (height - total_text_height) // 2 - int(height * 0.05)

    # Vẽ từng dòng — Shadow + Text trắng
    current_y = start_y
    for i, line in enumerate(lines):
        lw = line_widths[i]
        x = (width - lw) // 2

        # Shadow (offset 3px)
        draw.text((x + 3, current_y + 3), line, fill=(0, 0, 0, 180), font=title_font)
        # Text chính — trắng sáng
        draw.text((x, current_y), line, fill=(255, 255, 255), font=title_font)

        current_y += line_heights[i] + 12

    # ═══════════════════════════════════════
    # Decorative line dưới title
    # ═══════════════════════════════════════
    line_y = current_y + int(height * 0.04)
    line_margin = int(width * 0.2)
    draw.line(
        [(line_margin, line_y), (width - line_margin, line_y)],
        fill=(120, 100, 200, 150),
        width=2
    )

    # Lưu
    img.convert('RGB').save(output_path, quality=95)
    print(f"   ✅ Intro title card: {os.path.basename(output_path)}")


def create_outro_card(output_path, width=None, height=None):
    """
    Tạo outro card "Cảm ơn đã xem".
    
    Args:
        output_path: Đường dẫn file output (.png)
        width: Chiều rộng (mặc định từ config)
        height: Chiều cao (mặc định từ config)
    """
    from PIL import Image, ImageDraw, ImageFont
    
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient background: Dark → Deep blue
    for y in range(height):
        ratio = y / height
        r = int(10 + 20 * ratio)
        g = int(8 + 12 * ratio)
        b = int(40 + 50 * (1 - ratio))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Overlay decorative
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Vòng tròn trang trí
    overlay_draw.ellipse(
        [width * 0.3, height * 0.35, width * 0.7, height * 0.65],
        fill=(80, 60, 160, 20)
    )

    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img)

    # Text chính
    main_font_size = int(height * 0.05)
    main_font = _get_font(main_font_size)

    # "Cảm ơn đã xem"
    main_text = "Cảm ơn đã xem"
    bbox = draw.textbbox((0, 0), main_text, font=main_font)
    tw = bbox[2] - bbox[0]
    tx = (width - tw) // 2
    ty = height // 2 - int(height * 0.06)

    # Shadow
    draw.text((tx + 3, ty + 3), main_text, fill=(0, 0, 0, 180), font=main_font)
    draw.text((tx, ty), main_text, fill=(255, 255, 255), font=main_font)

    # Decorative line
    line_y = ty + int(height * 0.11)
    line_margin = int(width * 0.25)
    draw.line(
        [(line_margin, line_y), (width - line_margin, line_y)],
        fill=(100, 80, 180, 150),
        width=2
    )

    # Lưu
    img.convert('RGB').save(output_path, quality=95)
    print(f"   ✅ Outro card: {os.path.basename(output_path)}")


def _get_font(size):
    """Tìm font Sans-Serif phù hợp trên macOS."""
    from PIL import ImageFont

    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

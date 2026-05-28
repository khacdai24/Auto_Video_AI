"""
Tạo Intro/Outro Title Card bằng Pillow.
Sử dụng hình ảnh nền AI (nếu có) + phủ lớp đen mờ + văn bản đậm chất lượng cao.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VIDEO_WIDTH, VIDEO_HEIGHT


def create_intro_card(title, output_path, bg_image_path=None, width=None, height=None):
    """
    Tạo intro title card. Sử dụng background AI nếu có, nếu không vẽ gradient.
    
    Args:
        title: Tiêu đề video (tiếng Việt)
        output_path: Đường dẫn file output (.png)
        bg_image_path: Đường dẫn ảnh nền AI (tùy chọn)
        width: Chiều rộng (mặc định từ config)
        height: Chiều cao (mặc định từ config)
    """
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    # 1. Load hoặc tạo background image
    img = None
    if bg_image_path and os.path.exists(bg_image_path):
        try:
            img = Image.open(bg_image_path).resize((width, height), Image.Resampling.LANCZOS)
            print(f"   🎨 Sử dụng ảnh nền AI cho Intro: {os.path.basename(bg_image_path)}")
        except Exception as e:
            print(f"   ⚠️ Lỗi load ảnh nền AI ({e}), sử dụng gradient fallback...")
            img = None

    if img is None:
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        # Gradient background: Deep blue → Purple → Dark
        for y in range(height):
            ratio = y / height
            r = int(15 + 40 * ratio)
            g = int(10 + 15 * ratio)
            b = int(60 + 80 * (1 - ratio))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Tạo lớp phủ mờ (dark overlay) giúp chữ trắng nổi bật và dễ đọc
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)

    # Phủ lớp đen bán trong suốt (nếu là ảnh AI thì phủ dày hơn để tăng độ tương phản)
    overlay_opacity = 115 if bg_image_path and os.path.exists(bg_image_path) else 40
    overlay_draw.rectangle([0, 0, width, height], fill=(0, 0, 0, overlay_opacity))

    # Vòng tròn trang trí mờ (chỉ vẽ nếu là nền gradient để tránh rối ảnh AI)
    if bg_image_path is None or not os.path.exists(bg_image_path):
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

    # 3. Title text — Lớn, nét đậm, viền đen sắc nét, căn giữa
    title_font_size = int(height * 0.055)
    title_font = _get_font(title_font_size, bold=True)

    # Wrap title thành các dòng ngắn (max 14 ký tự cho portrait)
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

    # Vẽ từng dòng — Viền đen dày (stroke) + Text trắng
    current_y = start_y
    stroke_width = max(2, int(title_font_size * 0.06))
    for i, line in enumerate(lines):
        lw = line_widths[i]
        x = (width - lw) // 2

        draw.text(
            (x, current_y), 
            line, 
            fill=(255, 255, 255), 
            font=title_font,
            stroke_width=stroke_width,
            stroke_fill=(0, 0, 0)
        )
        current_y += line_heights[i] + 12

    # 4. Decorative line dưới title
    line_y = current_y + int(height * 0.04)
    line_margin = int(width * 0.2)
    draw.line(
        [(line_margin, line_y), (width - line_margin, line_y)],
        fill=(255, 255, 255, 120),
        width=2
    )

    # Lưu
    img.convert('RGB').save(output_path, quality=95)
    print(f"   ✅ Intro title card: {os.path.basename(output_path)}")


def create_outro_card(output_path, bg_image_path=None, width=None, height=None):
    """
    Tạo outro card "Cảm ơn đã xem". Sử dụng background AI nếu có, nếu không vẽ gradient.
    
    Args:
        output_path: Đường dẫn file output (.png)
        bg_image_path: Đường dẫn ảnh nền AI (tùy chọn)
        width: Chiều rộng (mặc định từ config)
        height: Chiều cao (mặc định từ config)
    """
    from PIL import Image, ImageDraw, ImageFont
    
    width = width or VIDEO_WIDTH
    height = height or VIDEO_HEIGHT

    # 1. Load hoặc tạo background image
    img = None
    if bg_image_path and os.path.exists(bg_image_path):
        try:
            img = Image.open(bg_image_path).resize((width, height), Image.Resampling.LANCZOS)
            print(f"   🎨 Sử dụng ảnh nền AI cho Outro: {os.path.basename(bg_image_path)}")
        except Exception as e:
            print(f"   ⚠️ Lỗi load ảnh nền AI ({e}), sử dụng gradient fallback...")
            img = None

    if img is None:
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        # Gradient background: Dark → Deep blue
        for y in range(height):
            ratio = y / height
            r = int(10 + 20 * ratio)
            g = int(8 + 12 * ratio)
            b = int(40 + 50 * (1 - ratio))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Tạo lớp phủ mờ
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    overlay_opacity = 115 if bg_image_path and os.path.exists(bg_image_path) else 40
    overlay_draw.rectangle([0, 0, width, height], fill=(0, 0, 0, overlay_opacity))

    # Vòng tròn trang trí (nếu dùng gradient)
    if bg_image_path is None or not os.path.exists(bg_image_path):
        overlay_draw.ellipse(
            [width * 0.3, height * 0.35, width * 0.7, height * 0.65],
            fill=(80, 60, 160, 20)
        )

    img = Image.alpha_composite(img.convert('RGBA'), overlay)
    draw = ImageDraw.Draw(img)

    # 3. Main text "Cảm ơn đã xem"
    main_font_size = int(height * 0.05)
    main_font = _get_font(main_font_size, bold=True)

    main_text = "Cảm ơn đã xem"
    bbox = draw.textbbox((0, 0), main_text, font=main_font)
    tw = bbox[2] - bbox[0]
    tx = (width - tw) // 2
    ty = height // 2 - int(height * 0.06)

    stroke_width = max(2, int(main_font_size * 0.06))
    draw.text(
        (tx, ty), 
        main_text, 
        fill=(255, 255, 255), 
        font=main_font,
        stroke_width=stroke_width,
        stroke_fill=(0, 0, 0)
    )

    # 4. Decorative line
    line_y = ty + int(height * 0.11)
    line_margin = int(width * 0.25)
    draw.line(
        [(line_margin, line_y), (width - line_margin, line_y)],
        fill=(255, 255, 255, 120),
        width=2
    )

    # Lưu
    img.convert('RGB').save(output_path, quality=95)
    print(f"   ✅ Outro card: {os.path.basename(output_path)}")


def _get_font(size, bold=False):
    """Tìm font chữ phù hợp trên macOS, hỗ trợ tuỳ chọn font Bold."""
    from PIL import ImageFont

    if bold:
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNS.ttf",
        ]
    else:
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

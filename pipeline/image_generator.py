"""
Step 4: Sinh hình ảnh bằng Pollinations.ai (miễn phí, không cần API key).
Input: visual_prompt (tiếng Anh)
Output: File .png

Sử dụng endpoint mới: https://image.pollinations.ai/prompt/...
Không chỉ định model cụ thể để dùng model miễn phí mặc định.
"""
import os
import sys
import time
import random
import urllib.parse

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    IMAGE_MODEL,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    SUBTITLE_FONT_SIZE_RATIO,
    SUBTITLE_Y_RATIO,
)


def generate_image(prompt, output_path, max_retries=3):
    """
    Sinh hình ảnh từ prompt bằng Pollinations.ai.

    Args:
        prompt: Mô tả hình ảnh bằng tiếng Anh
        output_path: Đường dẫn file output (.png)
        max_retries: Số lần thử lại nếu thất bại
    """
    # Rút gọn prompt nếu quá dài (URL quá dài có thể bị lỗi)
    if len(prompt) > 300:
        prompt = prompt[:300]

    # Thêm style enhancement
    enhanced_prompt = f"{prompt}, high quality, detailed"

    # Encode prompt cho URL
    encoded_prompt = urllib.parse.quote(enhanced_prompt)

    # Seed ngẫu nhiên
    seed = random.randint(1, 999999)

    # Giữ đúng tỷ lệ dọc 9:16. Giới hạn cạnh lớn ở 1280 để tránh lỗi quota/402,
    # nhưng không ép về 1280x720 vì sẽ làm ảnh nguồn sai tỷ lệ và gây crop rung.
    width, height = _get_portrait_request_size()

    for attempt in range(1, max_retries + 1):
        seed = random.randint(1, 999999)

        # Thử nhiều endpoint format
        urls = [
            # Endpoint chính
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}&seed={seed}&model={IMAGE_MODEL}&enhance=true&nologo=true",
            # Endpoint mới (gen.pollinations.ai)
            f"https://gen.pollinations.ai/image/{encoded_prompt}"
            f"?width={width}&height={height}&seed={seed}&model={IMAGE_MODEL}&enhance=true&nologo=true",
        ]

        url = urls[0] if attempt <= 2 else urls[1]

        try:
            print(f"   📡 Đang tải ảnh từ Pollinations.ai (lần {attempt}/{max_retries})...")
            response = requests.get(url, timeout=90, allow_redirects=True)

            # Nếu 402, thử endpoint khác
            if response.status_code == 402:
                if attempt < max_retries:
                    print(f"   ⚠️ Endpoint trả về 402, thử endpoint khác...")
                    # Thử endpoint khác
                    alt_url = urls[1] if url == urls[0] else urls[0]
                    response = requests.get(alt_url, timeout=90, allow_redirects=True)
                    if response.status_code == 402:
                        raise requests.exceptions.HTTPError(f"402 Payment Required")

            response.raise_for_status()

            # Kiểm tra response có phải ảnh không
            content_type = response.headers.get('content-type', '')
            if len(response.content) < 1000 and 'image' not in content_type:
                raise ValueError(f"Response không phải ảnh (size: {len(response.content)} bytes)")

            # Lưu ảnh
            with open(output_path, 'wb') as f:
                f.write(response.content)

            file_size_kb = os.path.getsize(output_path) / 1024
            print(f"   ✅ Đã lưu ảnh ({file_size_kb:.0f} KB)")

            # Chờ giữa các request để tránh rate limit
            time.sleep(3)
            return

        except Exception as e:
            print(f"   ⚠️ Lần {attempt} thất bại: {e}")
            if attempt < max_retries:
                wait = attempt * 8
                print(f"   ⏳ Chờ {wait}s rồi thử lại...")
                time.sleep(wait)
            else:
                print(f"   ❌ Không thể tải ảnh sau {max_retries} lần thử")
                # Tạo ảnh placeholder thay vì crash
                _create_placeholder_image(output_path, prompt, width, height)


def _create_placeholder_image(output_path, prompt, width=1280, height=720):
    """Tạo ảnh placeholder nếu API thất bại, để pipeline không bị dừng."""
    try:
        from PIL import Image, ImageDraw, ImageFont

        # Tạo ảnh gradient đẹp
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Gradient background (dark blue to dark purple)
        for y in range(height):
            r = int(20 + (40 - 20) * y / height)
            g = int(20 + (20 - 20) * y / height)
            b = int(80 + (120 - 80) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # Text
        text = prompt[:80] + "..." if len(prompt) > 80 else prompt
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except Exception:
            font = ImageFont.load_default()

        # Vẽ text ở giữa
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = height // 2 - 12
        draw.text((x, y), text, fill=(200, 200, 255), font=font)

        img.save(output_path)
        print(f"   🎨 Đã tạo ảnh placeholder thay thế")
    except Exception as e2:
        print(f"   ❌ Không thể tạo placeholder: {e2}")
        sys.exit(1)


def _get_portrait_request_size():
    """Tính kích thước request ảnh theo tỷ lệ video dọc, cạnh lớn tối đa 1280."""
    max_width = min(IMAGE_WIDTH, 1280)
    max_height = min(IMAGE_HEIGHT, 1280)
    aspect_ratio = VIDEO_WIDTH / VIDEO_HEIGHT

    height = max_height
    width = int(round(height * aspect_ratio))

    if width > max_width:
        width = max_width
        height = int(round(width / aspect_ratio))

    # Encoder H.264 thích kích thước chẵn; giữ luôn từ đầu để giảm resize lẻ.
    width = max(2, width - (width % 2))
    height = max(2, height - (height % 2))
    return width, height


def draw_subtitle_on_image_obj(img, subtitle_text):
    """
    Vẽ phụ đề trực tiếp lên một đối tượng PIL Image.
    Trả về ảnh đã được vẽ phụ đề.
    """
    if not subtitle_text:
        return img
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        # Tạo bản sao RGBA để vẽ overlay trong suốt
        img_rgba = img.convert('RGBA')
        draw = ImageDraw.Draw(img_rgba)
        width, height = img_rgba.size

        # Cấu hình text — dùng tỷ lệ từ config
        font_size = int(height * SUBTITLE_FONT_SIZE_RATIO)
        
        # Thử tìm font chữ Bold trên macOS để làm phụ đề nổi bật
        font = None
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNS.ttf"
        ]
        for p in font_paths:
            if os.path.exists(p):
                try:
                    font = ImageFont.truetype(p, font_size)
                    break
                except Exception:
                    continue
        if not font:
            font = ImageFont.load_default()

        # Wrap text thành các dòng tối đa ~40 ký tự tiếng Việt
        lines = textwrap.wrap(subtitle_text, width=40)
        
        # Tính kích thước khối chữ
        line_heights = []
        line_widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])
            
        max_line_width = max(line_widths) if line_widths else 0
        total_height = sum(line_heights) + (8 * (len(lines) - 1)) # spacing

        # Chọn vị trí: Cách đáy ảnh theo tỷ lệ từ config
        padding_y = int(height * SUBTITLE_Y_RATIO)
        box_y1 = height - padding_y - total_height - 10
        box_y2 = height - padding_y + 10
        box_x1 = (width - max_line_width) // 2 - 20
        box_x2 = (width + max_line_width) // 2 + 20
        
        # Giới hạn box_x1, box_x2 trong khoảng ảnh
        box_x1 = max(10, box_x1)
        box_x2 = min(width - 10, box_x2)

        # Vẽ nền đen bán trong suốt cực kỳ nhẹ (khoảng 33% opacity)
        overlay = Image.new('RGBA', img_rgba.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rounded_rectangle(
            [box_x1, box_y1, box_x2, box_y2],
            radius=8,
            fill=(0, 0, 0, 85)
        )
        img_rgba = Image.alpha_composite(img_rgba, overlay)
        draw = ImageDraw.Draw(img_rgba)

        # Vẽ chữ màu trắng với viền đen dày (stroke outline) đè lên trên nền mờ
        current_y = box_y1 + 8
        stroke_width = max(3, int(font_size * 0.09))
        for i, line in enumerate(lines):
            line_w = line_widths[i]
            x = (width - line_w) // 2
            draw.text(
                (x, current_y), 
                line, 
                fill=(255, 255, 255), 
                font=font,
                stroke_width=stroke_width,
                stroke_fill=(0, 0, 0)
            )
            current_y += line_heights[i] + 8

        return img_rgba.convert('RGB')
    except Exception as e:
        print(f"      ⚠️ Không thể vẽ phụ đề lên đối tượng ảnh: {e}")
        return img


def burn_subtitle_to_image(image_path, subtitle_text):
    """
    Vẽ phụ đề trực tiếp lên hình ảnh tĩnh (burned-in subtitle).
    Giúp hỗ trợ phụ đề ngay cả khi FFmpeg không có filter 'subtitles' hoặc 'drawtext'.
    """
    if not subtitle_text:
        return
    try:
        from PIL import Image
        img = Image.open(image_path)
        img_with_sub = draw_subtitle_on_image_obj(img, subtitle_text)
        img_with_sub.save(image_path)
        print(f"      📝 Đã burn phụ đề vào ảnh (Bold + Outline): \"{subtitle_text}\"")
    except Exception as e:
        print(f"      ⚠️ Không thể burn phụ đề vào ảnh: {e}")

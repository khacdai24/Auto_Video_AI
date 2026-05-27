"""
Step 6: Sinh file phụ đề SRT từ dữ liệu kịch bản.
Input: Danh sách scenes với subtitle và duration
Output: File .srt
"""


def generate_srt(scenes, output_path):
    """
    Tạo file phụ đề SRT từ danh sách scenes.

    Args:
        scenes: list of dict, mỗi scene có 'subtitle' và 'actual_duration'
        output_path: Đường dẫn file output (.srt)
    """
    srt_content = []
    current_time = 0.0

    for i, scene in enumerate(scenes):
        subtitle_text = scene.get("subtitle", scene.get("narration", ""))
        duration = scene.get("actual_duration", 8.0)

        start_time = current_time
        end_time = current_time + duration

        # Format timestamp: HH:MM:SS,mmm
        start_str = _format_srt_time(start_time)
        end_str = _format_srt_time(end_time)

        srt_entry = f"{i + 1}\n{start_str} --> {end_str}\n{subtitle_text}\n"
        srt_content.append(srt_entry)

        current_time = end_time

    # Ghi file SRT
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(srt_content))


def _format_srt_time(seconds):
    """
    Chuyển đổi giây thành format SRT: HH:MM:SS,mmm

    Args:
        seconds: Thời gian tính bằng giây (float)

    Returns:
        str: "HH:MM:SS,mmm"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

"""
Step 3: Tính thời lượng file audio.
Input: File .mp3
Output: Duration (giây)
"""
from pydub import AudioSegment


def get_audio_duration(audio_path):
    """
    Đọc thời lượng file audio.

    Args:
        audio_path: Đường dẫn file .mp3

    Returns:
        float: Thời lượng tính bằng giây
    """
    audio = AudioSegment.from_file(audio_path)
    duration = audio.duration_seconds
    return round(duration, 2)

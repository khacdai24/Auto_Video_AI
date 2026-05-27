# 🎬 AI Video Generation Pipeline v2.0

## 1. Tổng quan dự án (Overview)
Đây là một hệ thống tự động hoàn toàn (100% tự động) dùng để tạo video ngắn dạng dọc (tỷ lệ 9:16, độ phân giải 720x1280) phù hợp cho các nền tảng như TikTok, YouTube Shorts, và Instagram Reels. 
Dự án được thiết kế với tiêu chí **100% Miễn phí (Zero-cost)** bằng cách tận dụng các API miễn phí và các công cụ mã nguồn mở.

## 2. Tính năng nổi bật (Key Features)
- **Chuẩn Video Dọc 9:16**: Tối ưu hiển thị cho nền tảng di động.
- **Tự động hóa 100%**: Chỉ cần nhập chủ đề (topic) và số cảnh (scenes), pipeline sẽ tự động viết kịch bản, đọc giọng nói, vẽ ảnh, làm hiệu ứng và ghép video.
- **Tiếng Việt hoàn chỉnh**: Hỗ trợ prompt tiếng Việt, sinh nội dung tiếng Việt và có sẵn giọng đọc AI tiếng Việt tự nhiên.
- **Hiệu ứng mượt mà**: Hiệu ứng Ken Burns (chỉ zoom in/out, không rung lắc) và Fade transitions (0.5s) giữa các cảnh.
- **Title Cards**: Tự động tạo Intro và Outro video chuyên nghiệp bằng Pillow (Gradient background, Text đổ bóng).
- **Âm thanh rõ ràng**: Ghép giọng đọc AI trực tiếp vào video, không thêm nhạc nền.
- **Cơ chế Fallback thông minh**: Tự động chuyển đổi giữa các Voice Engine hoặc Image endpoints nếu gặp lỗi giới hạn truy cập (Rate Limit).

## 3. Luồng hoạt động (8-Step Pipeline)
Dự án thực thi tuần tự qua 8 bước trong file `main.py`:
1. **Sinh kịch bản (`story_generator.py`)**: Gửi topic tới Google Gemini API (2.5 Flash Lite / 1.5 Flash) để lấy kịch bản JSON (Tiêu đề, lời thoại, mô tả hình ảnh tiếng Anh, loại hiệu ứng camera).
2. **Tạo giọng đọc (`voice_generator.py`)**: Dùng `edge-tts` để chuyển đổi lời thoại thành file `.mp3` (tăng tốc độ đọc +15% so với gốc).
3. **Tạo Title Cards (`title_card.py` & `video_animator.py`)**: Dùng Pillow vẽ ảnh Intro/Outro và FFmpeg tạo thành video ngắn 3 giây.
4. **Sinh hình ảnh (`image_generator.py`)**: Gọi API `Pollinations.ai` để sinh ảnh dọc từ prompt tiếng Anh. Đồng thời dùng Pillow để "burn" cứng phụ đề (subtitles) trực tiếp lên ảnh.
5. **Tạo hiệu ứng video (`video_animator.py`)**: Render chuyển động zoom in/zoom out từ ảnh tĩnh rồi mã hóa bằng FFmpeg.
6. **Tạo file phụ đề (`subtitle_generator.py`)**: Tạo file `.srt` dự phòng.
7. **Tạo audio im lặng**: Dùng FFmpeg/Pydub sinh audio trống (silence) 3s cho Intro/Outro.
8. **Ghép video (`video_merger.py`)**: 
   - Ghép nối các scene videos lại bằng `xfade` (fade transition).
   - Ghép các scene audios.
   - Ghép giọng đọc vào video để xuất file `final.mp4`.

## 4. Công nghệ & Thư viện (Tech Stack)
- **Ngôn ngữ**: Python 3
- **Xử lý Video/Audio cốt lõi**: `FFmpeg` (subprocess)
- **Sinh nội dung Text (LLM)**: `google-generativeai` (Gemini API)
- **Sinh giọng đọc (TTS)**: `edge-tts` (Microsoft Edge Voice), `gTTS` (Google TTS - dùng làm fallback)
- **Sinh hình ảnh**: `Pollinations.ai` (Free HTTP API)
- **Xử lý ảnh & Subtitle**: `Pillow` (PIL)
- **Xử lý âm thanh**: `pydub`

## 5. Cấu trúc thư mục (Folder Structure)
```text
Auto_Video/
├── config.py                 # File cấu hình trung tâm (Độ phân giải, bitrate, font chữ, TTS rate)
├── main.py                   # Điểm neo chạy chương trình, quản lý luồng 8 bước
├── requirements.txt          # Danh sách thư viện Python cần thiết
├── README.md                 # Tài liệu này
├── pipeline/                 # Chứa các module xử lý riêng biệt
│   ├── story_generator.py    # Xử lý kết nối Gemini API, parser JSON kịch bản
│   ├── voice_generator.py    # Chạy edge-tts qua subprocess độc lập (cách ly gRPC) + fallback gTTS
│   ├── image_generator.py    # Gọi API Pollinations.ai (có retry) + burn phụ đề bằng Pillow
│   ├── video_animator.py     # Render hiệu ứng Ken Burns zoom in/out
│   ├── video_merger.py       # Xử lý filter xfade, ghép giọng đọc, xuất final.mp4
│   ├── title_card.py         # Code vẽ Intro/Outro background bằng thuật toán màu gradient (Pillow)
│   ├── subtitle_generator.py # Tạo file .srt chuẩn
│   └── audio_utils.py        # Các hàm tiện ích đọc độ dài audio
└── output/                   # Nơi chứa kết quả chạy. Mỗi video tạo 1 thư mục con (VD: output/ten-chu-de/)
    └── <slug-chu-de>/
        ├── final.mp4         # KẾT QUẢ CUỐI CÙNG
        ├── story.json        # Kịch bản raw sinh bởi AI
        ├── scene_X.png       # Ảnh gốc từng cảnh
        ├── scene_X.mp3       # File audio từng cảnh
        └── scene_X.mp4       # Video riêng của từng cảnh
```

## 6. Hướng dẫn sử dụng & Cài đặt
### Yêu cầu hệ thống:
- Python 3.9+
- FFmpeg (phải có sẵn trên biến môi trường hệ thống. Mac: `brew install ffmpeg`)
- API Key của Google Gemini (đặt trong biến môi trường `GEMINI_API_KEY`)

### Chạy lệnh:
1. Mở Terminal tại thư mục `Auto_Video`
2. Kích hoạt môi trường ảo: `source venv/bin/activate`
3. Chạy script (Nên kèm biến môi trường chống lỗi gRPC):
   ```bash
   GRPC_ENABLE_FORK_SUPPORT=0 python main.py --topic "Vũ trụ bí ẩn" --scenes 5
   ```
   *(Nếu không truyền `--topic`, script sẽ tạm dừng và hỏi bạn nhập vào).*

## 7. Các cơ chế khắc phục lỗi đang áp dụng (Dành cho AI tham khảo)
Nếu bạn là một Trợ lý AI đang được yêu cầu fix lỗi hoặc nâng cấp repo này, hãy lưu ý các giải pháp đã được implement thành công:
1. **Lỗi `gRPC fork()` của Python macOS**: Khi dùng `edge-tts` (có import grpc) cùng với `google.generativeai`, việc gọi `subprocess` sinh ra lỗi hanging (tiến trình bị kẹt). 
   - *Cách giải quyết hiện tại*: Module `voice_generator.py` chạy edge-tts bằng một dòng lệnh inline python (`subprocess.run([sys.executable, "-c", script])`), kết hợp truyền biến môi trường `GRPC_ENABLE_FORK_SUPPORT="0"`.
2. **Lỗi Edge-TTS bị Rate Limit (`No audio was received`)**: Server Microsoft thường hay block request nếu gửi nhiều audio cùng lúc.
   - *Cách giải quyết hiện tại*: Pipeline có cơ chế Retry + Delay (tăng dần 5s, 10s, 15s). Nếu thất bại 3 lần, code sẽ **TỰ ĐỘNG fallback sang thư viện `gTTS`** (Google Translate) để video không bao giờ bị fail giữa chừng.
3. **Lỗi FFmpeg thiếu thư viện `libass` trên Mac (`Error parsing filterchain subtitles=...`)**:
   - *Cách giải quyết hiện tại*: Ảnh sinh ra từ Pollinations.ai đã được "burn" sẵn text phụ đề lên trên nó thông qua `Pillow` trong hàm `image_generator.py`. Bước ghép phụ đề srt bằng FFmpeg trong `video_merger.py` nếu lỗi sẽ bắt `try/except` và bỏ qua, sử dụng video hình ảnh đã có chữ sẵn làm Fallback.

## 8. Hướng nâng cấp trong tương lai (Future Works)
- Cho phép người dùng chọn style ảnh (Anime, Realistic, 3D, Cyberpunk) qua tham số truyền vào `--style`.
- Nâng cấp độ sắc nét của hình ảnh bằng các thư viện AI Upscaler.
- Cho phép bật/tắt nhạc nền hoặc thêm nhạc nền tùy chọn.
- Cho phép tự động thêm watermark hoặc logo của người tạo vào Video.

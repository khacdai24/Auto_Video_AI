<div align="center">

# 🎬 Auto Video AI — Pipeline v2.1

### Tự động tạo video ngắn dọc 9:16 từ ý tưởng văn bản — 100% Miễn phí

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Cost](https://img.shields.io/badge/Chi_phí-$0-brightgreen?style=for-the-badge)]()

**TikTok** • **YouTube Shorts** • **Instagram Reels** • **Facebook Reels**

---

*Từ một file kịch bản đơn giản → Video hoàn chỉnh có giọng đọc AI, hình ảnh AI, hiệu ứng zoom và phụ đề chuyên nghiệp — tất cả chỉ với một dòng lệnh.*

</div>

---

## 📑 Mục lục

- [✨ Tính năng](#-tính-năng)
- [🏗️ Kiến trúc Pipeline](#️-kiến-trúc-pipeline)
- [⚡ Cài đặt nhanh](#-cài-đặt-nhanh)
- [🚀 Sử dụng](#-sử-dụng)
- [📝 Format file `idea.txt`](#-format-file-ideatxt)
- [⚙️ Cấu hình](#️-cấu-hình)
- [📂 Cấu trúc dự án](#-cấu-trúc-dự-án)
- [🛡️ Cơ chế chống lỗi](#️-cơ-chế-chống-lỗi)
- [🗺️ Roadmap](#️-roadmap)

---

## ✨ Tính năng

| Tính năng | Mô tả |
|-----------|--------|
| 📱 **Video dọc 9:16** | Tối ưu cho TikTok, Shorts, Reels — 720×1280px |
| 🤖 **2 chế độ hoạt động** | Đọc kịch bản từ `idea.txt` (mặc định) hoặc sinh tự động bằng Gemini AI |
| 🇻🇳 **Tiếng Việt hoàn chỉnh** | Kịch bản, giọng đọc, phụ đề đều hỗ trợ tiếng Việt |
| 🖼️ **Ảnh AI Pollinations.ai** | Sinh hình ảnh chất lượng cao từ prompt tiếng Anh — không cần API key |
| 🎨 **Intro & Outro AI** | Tạo title card bằng ảnh nền AI sinh theo chủ đề video + overlay văn bản sang trọng |
| 🎙️ **Giọng đọc AI tự nhiên** | Edge-TTS (Microsoft) + Fallback gTTS (Google) — tốc độ tùy chỉnh |
| 🎥 **Hiệu ứng Ken Burns** | Zoom in / Zoom out mượt mà — không rung lắc |
| ✨ **Phụ đề Bold Outline** | Chữ đậm viền đen dày, vị trí tối ưu trên nền mờ (tránh UI overlay) |
| 🔄 **Fade Transitions** | Chuyển cảnh mượt mà 0.5s giữa các scene |
| 🛡️ **Fallback thông minh** | Tự động chuyển engine/endpoint khi gặp rate limit hoặc lỗi API |
| 💰 **100% Miễn phí** | Không tốn bất kỳ chi phí nào — zero API cost |

---

## 🏗️ Kiến trúc Pipeline

Pipeline thực thi tuần tự qua **8 bước tự động**:

```
┌─────────────────────────────────────────────────────────┐
│                    📄 INPUT                             │
│         idea.txt (mặc định)  hoặc  --topic "..."        │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 1: Đọc/Sinh kịch bản │
        │  idea_parser / Gemini API   │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 2: Tạo giọng đọc     │
        │  edge-tts → gTTS fallback   │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 3: Intro & Outro AI   │
        │  Pollinations + Pillow      │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 4: Sinh hình ảnh AI   │
        │  Pollinations.ai + Subtitle │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 5: Hiệu ứng video    │
        │  FFmpeg Ken Burns zoom      │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 6: File phụ đề .srt   │
        │  subtitle_generator         │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 7: Audio im lặng      │
        │  Intro/Outro padding         │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │  STEP 8: Ghép video final   │
        │  xfade + audio merge        │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │     🎬 OUTPUT: final.mp4    │
        │     Video dọc 9:16 hoàn chỉnh│
        └─────────────────────────────┘
```

### Chi tiết từng bước

| Step | Module | Chức năng |
|------|--------|-----------|
| 1 | `idea_parser.py` / `story_generator.py` | Parse file `idea.txt` hoặc gọi Gemini API sinh kịch bản JSON |
| 2 | `voice_generator.py` | Chuyển lời thoại → file `.mp3` bằng Edge-TTS (fallback gTTS) |
| 3 | `title_card.py` + `image_generator.py` | Sinh ảnh nền AI cho Intro/Outro + phủ overlay + vẽ tiêu đề |
| 4 | `image_generator.py` | Sinh ảnh AI từ prompt + burn phụ đề Bold viền đen lên ảnh |
| 5 | `video_animator.py` | Render hiệu ứng Ken Burns (zoom in/out) từ ảnh tĩnh bằng FFmpeg |
| 6 | `subtitle_generator.py` | Tạo file `.srt` chuẩn (dự phòng) |
| 7 | `main.py` | Tạo audio im lặng 3s cho Intro/Outro |
| 8 | `video_merger.py` | Ghép toàn bộ scenes + fade transitions + audio → `final.mp4` |

---

## ⚡ Cài đặt nhanh

### Yêu cầu hệ thống

| Yêu cầu | Chi tiết |
|----------|----------|
| **OS** | macOS / Linux / Windows |
| **Python** | 3.9+ |
| **FFmpeg** | Phải cài sẵn trên PATH |
| **Kết nối mạng** | Cần Internet cho API sinh ảnh và giọng đọc |
| **Dung lượng** | ~500MB (bao gồm venv) |

### Bước 1: Cài FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

### Bước 2: Thiết lập dự án

```bash
# Clone/tải dự án
cd Auto_Video

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# Cài đặt thư viện
pip install -r requirements.txt
```

### Bước 3: Cấu hình API Key (Tùy chọn)

Chỉ cần nếu sử dụng **chế độ Gemini** (`--topic`). Lấy key miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey):

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Hoặc chỉnh trực tiếp trong `config.py`.

---

## 🚀 Sử dụng

### Chế độ 1: Đọc kịch bản từ `idea.txt` ⭐ Khuyến nghị

Viết sẵn kịch bản vào file `idea.txt` rồi chạy — **không cần Gemini API key**:

```bash
source venv/bin/activate
GRPC_ENABLE_FORK_SUPPORT=0 python main.py
```

### Chế độ 2: Sinh kịch bản tự động bằng Gemini AI

Chỉ cần nhập chủ đề, AI tự viết kịch bản hoàn chỉnh:

```bash
GRPC_ENABLE_FORK_SUPPORT=0 python main.py --topic "Vũ trụ bí ẩn" --scenes 5
```

### Chế độ 3: Đọc từ file kịch bản tùy chỉnh

```bash
GRPC_ENABLE_FORK_SUPPORT=0 python main.py --idea my_custom_script.txt
```

### Tham số dòng lệnh

| Tham số | Mặc định | Mô tả |
|---------|----------|-------|
| `--topic` | *(không có)* | Chủ đề video — kích hoạt chế độ Gemini AI |
| `--scenes` | `5` | Số cảnh (chỉ áp dụng khi dùng `--topic`) |
| `--idea` | `idea.txt` | Đường dẫn file kịch bản tùy chỉnh |

> **💡 Tip:** Biến `GRPC_ENABLE_FORK_SUPPORT=0` là bắt buộc trên macOS để tránh lỗi `gRPC fork()` khi chạy subprocess.

---

## 📝 Format file `idea.txt`

File `idea.txt` là cách đơn giản nhất để tạo video — bạn hoàn toàn kiểm soát nội dung.

### Cấu trúc cơ bản

```text
# VIDEO: Tiêu đề video của bạn

## Thời gian: 00:00 - 00:04
Lời thoại (Voiceover):
"Lời thoại tiếng Việt cho cảnh này..."

Gợi ý hình ảnh cho AI (Visual Prompt):
English image description for AI generation here...

Camera: zoom_in

---

## Thời gian: 00:05 - 00:09
Lời thoại (Voiceover):
"Lời thoại tiếng Việt cho cảnh tiếp theo..."

Gợi ý hình ảnh cho AI (Visual Prompt):
Another English image description...

Camera: zoom_out

---
```

### Các trường tùy chọn nâng cao

```text
# VIDEO: Tiêu đề video
# INTRO PROMPT: Cinematic dark moody background, vertical 9:16, no text
# OUTRO PROMPT: Beautiful sunrise over mountains, vertical 9:16, no text

## Thời gian: 00:00 - 00:04
Lời thoại (Voiceover):
"Lời thoại..."

Phụ đề:
Phụ đề tùy chỉnh ngắn gọn

Gợi ý hình ảnh cho AI (Visual Prompt):
English prompt...

Camera: zoom_in

---
```

### Giải thích các trường

| Trường | Bắt buộc | Mô tả |
|--------|----------|-------|
| `# VIDEO:` | ✅ | Tiêu đề video — hiển thị trên Intro card |
| `# INTRO PROMPT:` | ❌ | Prompt sinh ảnh nền Intro (mặc định lấy từ Scene 1) |
| `# OUTRO PROMPT:` | ❌ | Prompt sinh ảnh nền Outro (mặc định lấy từ Scene cuối) |
| `## Thời gian:` | ✅ | Mốc thời gian tham khảo cho cảnh |
| `Lời thoại (Voiceover):` | ✅ | Lời thoại tiếng Việt — được chuyển thành giọng đọc AI |
| `Phụ đề:` / `Subtitle:` | ❌ | Phụ đề tùy chỉnh (mặc định tự tóm tắt từ lời thoại) |
| `Gợi ý hình ảnh cho AI (Visual Prompt):` | ✅ | Mô tả hình ảnh **bằng tiếng Anh** cho AI sinh ảnh |
| `Camera:` | ❌ | `zoom_in` hoặc `zoom_out` (mặc định xen kẽ tự động) |
| `---` | ✅ | Dấu phân cách giữa các cảnh |

---

## ⚙️ Cấu hình

Toàn bộ cấu hình nằm trong file [`config.py`](config.py):

### 🎬 Video

| Biến | Giá trị | Mô tả |
|------|---------|-------|
| `VIDEO_WIDTH` | `720` | Chiều rộng video (px) |
| `VIDEO_HEIGHT` | `1280` | Chiều cao video (px) |
| `VIDEO_FPS` | `30` | Tốc độ khung hình |
| `VIDEO_BITRATE` | `"3M"` | Bitrate video (3 Mbps) |

### 🎙️ Giọng đọc

| Biến | Giá trị | Mô tả |
|------|---------|-------|
| `TTS_VOICE` | `"vi-VN-NamMinhNeural"` | Giọng đọc mặc định (nam, Việt Nam) |
| `TTS_RATE` | `"+15%"` | Tốc độ đọc nhanh hơn 15% |

**Giọng đọc khả dụng:**
- `vi-VN-NamMinhNeural` — Nam, tiếng Việt
- `vi-VN-HoaiMyNeural` — Nữ, tiếng Việt
- `en-US-JennyNeural` — Nữ, tiếng Anh
- `en-US-GuyNeural` — Nam, tiếng Anh

### 🖼️ Sinh ảnh

| Biến | Giá trị | Mô tả |
|------|---------|-------|
| `IMAGE_WIDTH` | `768` | Chiều rộng ảnh gốc |
| `IMAGE_HEIGHT` | `1344` | Chiều cao ảnh gốc (dư biên cho zoom) |
| `IMAGE_MODEL` | `"flux-realism"` | Model sinh ảnh trên Pollinations.ai |

**Model sinh ảnh khả dụng:**
- `flux` — Mặc định, cân bằng chất lượng/tốc độ
- `flux-realism` — Chuyên ảnh thực tế
- `flux-anime` — Phong cách anime
- `flux-3d` — Phong cách 3D render
- `turbo` — Tốc độ nhanh

### 📝 Phụ đề

| Biến | Giá trị | Mô tả |
|------|---------|-------|
| `SUBTITLE_FONT_SIZE_RATIO` | `0.025` | Tỷ lệ font (~32px trên video 1280px) |
| `SUBTITLE_Y_RATIO` | `0.20` | Vị trí phụ đề (20% từ đáy — tối ưu cho các MXH) |

---

## 📂 Cấu trúc dự án

```
Auto_Video/
├── 📄 config.py                  # Cấu hình trung tâm
├── 🚀 main.py                    # Entry point — quản lý pipeline 8 bước
├── 📋 idea.txt                   # File kịch bản mặc định
├── 📦 requirements.txt           # Thư viện Python
├── 📖 README.md                  # Tài liệu này
├── 🧹 CLEANUP_MANIFEST.md        # Danh sách files/packages đã cài
│
├── 📁 pipeline/                   # Các module xử lý
│   ├── idea_parser.py            # Parse file idea.txt → story dict
│   ├── story_generator.py        # Kết nối Gemini API, sinh kịch bản JSON
│   ├── voice_generator.py        # Edge-TTS subprocess + gTTS fallback
│   ├── image_generator.py        # Pollinations.ai API + burn phụ đề Bold
│   ├── video_animator.py         # FFmpeg Ken Burns zoom in/out
│   ├── video_merger.py           # Ghép scenes + xfade + audio → final.mp4
│   ├── title_card.py             # Intro/Outro với AI background + overlay
│   ├── subtitle_generator.py     # Tạo file .srt chuẩn
│   └── audio_utils.py            # Tiện ích đọc duration audio
│
├── 📁 output/                     # Kết quả video
│   └── <slug-chu-de>/
│       ├── 🎬 final.mp4          # VIDEO HOÀN CHỈNH
│       ├── 📋 story.json         # Kịch bản JSON
│       ├── 🖼️ scene_intro.png    # Ảnh Intro (AI generated)
│       ├── 🖼️ scene_outro.png    # Ảnh Outro (AI generated)
│       ├── 🖼️ scene_X.png       # Ảnh từng cảnh
│       ├── 🎵 scene_X.mp3       # Audio từng cảnh
│       └── 🎥 scene_X.mp4       # Video từng cảnh
│
└── 📁 venv/                       # Môi trường ảo Python
```

---

## 🛠️ Tech Stack

| Công nghệ | Vai trò | Chi phí |
|------------|---------|---------|
| **Python 3** | Ngôn ngữ chính | Miễn phí |
| **FFmpeg** | Render video, audio, hiệu ứng | Miễn phí |
| **Pollinations.ai** | Sinh hình ảnh AI từ text prompt | Miễn phí |
| **Edge-TTS** | Giọng đọc AI (Microsoft Neural) | Miễn phí |
| **gTTS** | Giọng đọc fallback (Google Translate) | Miễn phí |
| **Google Gemini** | Sinh kịch bản tự động (tùy chọn) | Miễn phí (free tier) |
| **Pillow (PIL)** | Vẽ phụ đề, title cards, overlay | Miễn phí |
| **pydub** | Xử lý audio (duration, silence) | Miễn phí |

---

## 🛡️ Cơ chế chống lỗi

Pipeline được thiết kế với nhiều lớp bảo vệ để đảm bảo **không bao giờ crash giữa chừng**:

### 1. Lỗi gRPC fork() trên macOS

**Triệu chứng:** Process bị treo (hang) khi dùng `edge-tts` subprocess cùng `google.generativeai`.

**Giải pháp:**
- Module `voice_generator.py` chạy edge-tts bằng subprocess riêng biệt với môi trường sạch
- Bắt buộc set biến `GRPC_ENABLE_FORK_SUPPORT=0` khi chạy

### 2. Edge-TTS Rate Limit

**Triệu chứng:** `No audio was received` — server Microsoft từ chối request.

**Giải pháp:**
- Retry tự động 3 lần với delay tăng dần (5s → 10s → 15s)
- Fallback sang `gTTS` (Google Translate TTS) nếu Edge-TTS thất bại hoàn toàn

### 3. Pollinations.ai Timeout / 402

**Triệu chứng:** Request ảnh bị timeout (>90s) hoặc trả về lỗi 402 Payment Required.

**Giải pháp:**
- Retry 3 lần với delay tăng dần
- Thử endpoint phụ (`gen.pollinations.ai`) khi endpoint chính thất bại
- Tạo ảnh placeholder (gradient) nếu tất cả đều thất bại để pipeline tiếp tục

### 4. FFmpeg thiếu libass (macOS)

**Triệu chứng:** `Error parsing filterchain subtitles=...` khi burn phụ đề bằng FFmpeg.

**Giải pháp:**
- Phụ đề đã được burn trực tiếp lên ảnh bằng Pillow (Bold + Stroke outline)
- FFmpeg subtitles filter chỉ là bước phụ — nếu lỗi sẽ bỏ qua mà không ảnh hưởng video

### 5. Gemini API Quota

**Triệu chứng:** Model chính hết quota (429 / RESOURCE_EXHAUSTED).

**Giải pháp:**
- Tự động thử lần lượt các model fallback: `gemini-1.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.0-flash-lite` → `gemini-1.5-flash-8b`

---

## 🗺️ Roadmap

- [ ] 🎨 Cho phép chọn style ảnh qua tham số `--style` (Anime, Realistic, 3D, Cyberpunk)
- [ ] 🔊 Hỗ trợ nhạc nền tùy chọn (BGM) với volume tự động giảm khi có giọng đọc
- [ ] 🏷️ Tự động thêm watermark/logo vào video
- [ ] 📊 Upscale ảnh AI bằng thư viện AI Upscaler
- [ ] 🌐 Hỗ trợ đa ngôn ngữ (Anh, Nhật, Hàn)
- [ ] 🖥️ Giao diện Web UI đơn giản để người dùng không cần dùng Terminal

---

<div align="center">

**Made with ❤️ — 100% Free & Open Source**

*Nếu dự án hữu ích, hãy ⭐ star repo này!*

</div>

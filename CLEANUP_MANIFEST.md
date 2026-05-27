# 🧹 Cleanup Manifest — Auto_Video Project

> File này ghi lại **tất cả** những gì được cài đặt và tải về cho dự án.
> Nếu muốn xoá sạch, chỉ cần chạy các lệnh trong mục "Xoá sạch" ở cuối file.

---

## 📊 Tổng quan dung lượng ước tính

| Thành phần | Dung lượng thực tế | Vị trí |
|------------|---------------------|--------|
| FFmpeg + dependencies (brew) | **99 MB** | `/opt/homebrew/Cellar/` |
| Python venv + packages | **210 MB** | `Auto_Video/venv/` |
| Project source code | ~50 KB | `Auto_Video/pipeline/`, `Auto_Video/main.py`... |
| Output videos (mỗi video) | ~10-50 MB | `Auto_Video/output/` |
| **Tổng (không tính output)** | **~310 MB** | |

---

## 1️⃣ Cài đặt hệ thống (qua Homebrew)

| Package | Version | Dung lượng | Mục đích |
|---------|---------|------------|----------|
| `ffmpeg` | 8.1.1 | 52 MB | Xử lý video, ghép video, burn subtitle |
| `dav1d` | 1.5.3 | ~1 MB | AV1 decoder (dependency) |
| `lame` | 3.100 | 2.3 MB | MP3 encoder (dependency) |
| `libvmaf` | 3.1.0 | 7.5 MB | Video quality metrics (dependency) |
| `libvpx` | 1.16.0 | 4.4 MB | VP8/VP9 codec (dependency) |
| `opus` | 1.6.1 | 1.1 MB | Audio codec (dependency) |
| `sdl2` | 2.32.10 | 6.7 MB | Media playback (dependency) |
| `svt-av1` | 4.1.0 | 3.1 MB | AV1 encoder (dependency) |
| `x264` | r3222 | 4.4 MB | H.264 encoder (dependency) |
| `x265` | 4.2 | 17 MB | H.265 encoder (dependency) |

**Vị trí cài:** `/opt/homebrew/Cellar/` (Apple Silicon Mac)

---

## 2️⃣ Python Virtual Environment

| Thành phần | Chi tiết |
|------------|----------|
| **Vị trí** | `/Users/khacdai24/Downloads/Project/Auto_Video/venv/` |
| **Dung lượng** | **210 MB** |
| **Python version** | Python 3.9.6 (`/usr/bin/python3`) |

### Các package Python (cài trong venv):

| Package | Version | Mục đích |
|---------|---------|----------|
| `edge-tts` | 7.2.8 | Text-to-Speech miễn phí (Microsoft Edge) |
| `pydub` | 0.25.1 | Đọc thời lượng file audio |
| `requests` | 2.32.5 | Gọi HTTP đến Pollinations.ai |
| `google-generativeai` | 0.8.6 | Gemini API free tier (sinh kịch bản) |
| `Pillow` | 11.3.0 | Xử lý ảnh |
| + 35 dependencies | — | aiohttp, grpcio, protobuf, cryptography, v.v. |

---

## 3️⃣ File dự án được tạo mới

```
Auto_Video/
├── main.py                          # [MỚI] Entry point
├── config.py                        # [MỚI] Cấu hình
├── requirements.txt                 # [MỚI] Danh sách packages
├── CLEANUP_MANIFEST.md              # [MỚI] File này
├── venv/                            # [MỚI] Virtual environment
│
├── pipeline/                        # [MỚI] Toàn bộ thư mục
│   ├── __init__.py
│   ├── story_generator.py
│   ├── voice_generator.py
│   ├── audio_utils.py
│   ├── image_generator.py
│   ├── video_animator.py
│   ├── subtitle_generator.py
│   └── video_merger.py
│
└── output/                          # [MỚI] Thư mục chứa video output
    └── {topic}/
        ├── story.json
        ├── scene_*.mp3
        ├── scene_*.png
        ├── scene_*.mp4
        ├── scene_*.srt
        └── final.mp4
```

**File có sẵn (KHÔNG ĐỤNG VÀO):**
- `_MConverter.eu_AI Video Generation Pipeline.md` (spec gốc)

---

## 4️⃣ Tải về khi chạy (runtime downloads)

| Thành phần | Nguồn | Khi nào | Lưu ở đâu |
|------------|-------|---------|------------|
| Hình ảnh AI | Pollinations.ai | Mỗi lần tạo video | `output/{topic}/scene_*.png` |
| File audio TTS | Microsoft Edge servers | Mỗi lần tạo video | `output/{topic}/scene_*.mp3` |

> Không có model AI nào được tải về máy. Tất cả đều gọi qua internet (Gemini API, Pollinations.ai, Edge TTS).

---

## ❌ Xoá sạch toàn bộ

Nếu dự án không hoàn thành như mong đợi, chạy các lệnh sau để xoá **tất cả**:

```bash
# 1. Xoá toàn bộ project files (venv, code, output) — giải phóng ~210 MB
cd /Users/khacdai24/Downloads/Project/Auto_Video
rm -rf venv/ pipeline/ output/ main.py config.py requirements.txt CLEANUP_MANIFEST.md

# 2. Gỡ FFmpeg + tất cả dependencies (~99 MB)
brew uninstall ffmpeg dav1d lame libvmaf libvpx opus sdl2 svt-av1 x264 x265

# 3. (Tuỳ chọn) Dọn cache brew
brew cleanup
```

> ⚠️ Lệnh trên sẽ GIỮ LẠI file spec gốc `_MConverter.eu_AI Video Generation Pipeline.md`

---

## 📝 Lịch sử thay đổi

| Ngày | Hành động | Chi tiết |
|------|-----------|----------|
| 2026-05-26 | Tạo manifest | Ghi nhận kế hoạch cài đặt |
| 2026-05-26 | Cài đặt hoàn tất | FFmpeg 8.1.1 + 9 deps, Python venv 210MB, 40 pip packages |

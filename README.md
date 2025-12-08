# UABE Dump Text Manager

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

**UABE Dump Text Manager** là một công cụ Python đơn giản nhưng mạnh mẽ, hỗ trợ các nhóm dịch thuật game (Localization/Modding) làm việc với các file Dump từ **UABE (Unity Assets Bundle Extractor)** hoặc **UABEAvalonia**.

Thay vì phải chỉnh sửa trực tiếp trên hàng trăm file text hỗn độn mã code, công cụ này giúp trích xuất toàn bộ văn bản cần dịch ra một file `JSON` duy nhất, và tự động nhập lại vào file Dump sau khi dịch xong.

## 🚀 Tính năng chính

* **Batch Extraction:** Tự động quét toàn bộ file `.txt` (Dump) trong thư mục gốc.
* **JSON Export:** Gom toàn bộ văn bản `m_Localized` vào duy nhất một file `.json` để dễ dàng quản lý và dịch thuật.
* **Safe Import:** Đọc file JSON đã dịch và chèn ngược lại vào cấu trúc file Dump gốc, giữ nguyên các thông số kỹ thuật (PathID, FileID, v.v...).
* **No Dependency:** Chạy ngay lập tức bằng Python thuần, không cần cài đặt thư viện ngoài.

## 📋 Yêu cầu hệ thống

* Python 3.x trở lên.
* Công cụ UABE hoặc UABEAvalonia (để tạo file Dump từ game).

## 🛠️ Cài đặt

1.  Clone repository này về máy hoặc tải file `.zip`:
    ```bash
    git clone [https://github.com/thuyetabd/ToolXoaDumpBundleUabea.git](https://github.com/thuyetabd/ToolXoaDumpBundleUabea.git)
    ```
2.  Đảm bảo máy đã cài Python.

## 📖 Hướng dẫn sử dụng

### Bước 1: Chuẩn bị file Dump
Sử dụng UABE/UABEAvalonia để **Export Dump** các file assets chứa ngôn ngữ (thường là `MonoBehaviour`). Đặt tất cả các file `.txt` này vào một thư mục (Ví dụ: `Input_Dumps`).

### Bước 2: Xuất văn bản (Extract Mode)
1.  Chạy file script:
    ```bash
    python tool_quan_ly_dich.py
    ```
2.  Chọn chế độ **1**.
3.  Nhập đường dẫn thư mục `Input_Dumps`.
4.  Nhập đường dẫn thư mục bạn muốn lưu file dịch (Ví dụ: `Project_Translation`).
5.  Tool sẽ tạo ra file `dich_tai_day.json`.

### Bước 3: Dịch thuật
Mở file `dich_tai_day.json` bằng VS Code, Notepad++ hoặc bất kỳ trình soạn thảo văn bản nào.
Cấu trúc file sẽ như sau:

```json
{
    "UI_MainMenu.txt": [
        "New Game",   <-- Sửa thành: "Game Mới"
        "Load Game"   <-- Sửa thành: "Tải Game"
    ]
}

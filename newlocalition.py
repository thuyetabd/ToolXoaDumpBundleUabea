import json
import sys
import os

# --- CẤU HÌNH ---
INPUT_FILE = 'data.json'          
OUTPUT_FILE = 'new_data.json'     
EXPORT_TXT = 'source_english.txt' 
IMPORT_TXT = 'translated.txt'     
LANG_INDEX = 0                    

# --- HÀM DUYỆT ĐỆ QUY ---
def traverse_json(node, operation, context, path=""):
    """
    node: Dữ liệu hiện tại
    operation: 'export' hoặc 'import'
    context: Biến lưu trữ chung
    path: Đường dẫn hiện tại (để debug lỗi)
    """
    
    # 1. Nếu là Dict
    if isinstance(node, dict):
        # Kiểm tra xem node này có chứa text không
        if 'texts' in node and isinstance(node['texts'], dict) and 'Array' in node['texts']:
            text_array = node['texts']['Array']
            
            if isinstance(text_array, list) and len(text_array) > LANG_INDEX:
                # --- EXPORT ---
                if operation == 'export':
                    raw_text = text_array[LANG_INDEX]
                    if raw_text is None: raw_text = ""
                    # QUAN TRỌNG: Thay thế xuống dòng thật bằng ký tự '\n'
                    safe_text = raw_text.replace('\n', '\\n')
                    context['lines'].append(safe_text)
                    
                # --- IMPORT ---
                elif operation == 'import':
                    current_idx = context['counter']
                    translated_lines = context['lines']
                    
                    if current_idx < len(translated_lines):
                        line_content = translated_lines[current_idx]
                        # QUAN TRỌNG: Đổi ngược '\n' thành xuống dòng thật
                        final_text = line_content.replace('\\n', '\n')
                        
                        text_array[LANG_INDEX] = final_text
                        context['counter'] += 1
                    else:
                        # Hết dòng trong file dịch nhưng JSON vẫn còn slot
                        if not context['error_shown']:
                            print(f"\n[LỖI] File dịch hết dòng tại vị trí JSON: {path}")
                            print(f"Nội dung gốc tại đây là: {text_array[LANG_INDEX]}")
                            context['error_shown'] = True
            return

        # Tiếp tục đào sâu
        for key, value in node.items():
            traverse_json(value, operation, context, path + f"['{key}']")

    # 2. Nếu là List
    elif isinstance(node, list):
        for index, item in enumerate(node):
            traverse_json(item, operation, context, path + f"[{index}]")

# --- XUẤT ---
def export_text():
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {INPUT_FILE}")
        return

    context = {'lines': []}
    print("Đang xuất dữ liệu (đã xử lý ký tự xuống dòng)...")
    traverse_json(data, 'export', context)

    with open(EXPORT_TXT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(context['lines']))
    
    print(f"-> Đã xuất {len(context['lines'])} dòng ra '{EXPORT_TXT}'.")
    print("LƯU Ý: Các chỗ xuống dòng đã được chuyển thành '\\n'. Đừng xóa chữ này khi dịch.")

# --- NHẬP ---
def import_text():
    if not os.path.exists(IMPORT_TXT):
        print(f"Lỗi: Không tìm thấy file '{IMPORT_TXT}'")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(IMPORT_TXT, 'r', encoding='utf-8') as f:
        # Đọc file và loại bỏ ký tự xuống dòng thừa ở cuối mỗi dòng text
        translated_lines = f.read().splitlines()

    context = {
        'lines': translated_lines,
        'counter': 0,
        'error_shown': False
    }

    print("Đang nhập dữ liệu...")
    traverse_json(data, 'import', context)

    # Tổng kết
    json_slots = context['counter']
    txt_lines = len(translated_lines)

    if json_slots == txt_lines:
        print(f"-> THÀNH CÔNG! Khớp hoàn toàn {json_slots} dòng.")
    else:
        print(f"\n-> CẢNH BÁO LỆCH DÒNG:")
        print(f"   - File Text có: {txt_lines} dòng")
        print(f"   - File JSON đã điền: {json_slots} dòng")
        if txt_lines > json_slots:
            print(f"   -> Dư {txt_lines - json_slots} dòng trong file Text chưa được điền.")
        else:
            print(f"   -> Thiếu {json_slots - txt_lines} dòng (JSON còn chỗ nhưng hết text).")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"-> Đã lưu file kết quả: '{OUTPUT_FILE}'")

# --- MAIN ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'export':
            export_text()
        elif mode == 'import':
            import_text()
        else:
            print("Sai lệnh.")
    else:
        print("Dùng: python to.py export HOẶC python to.py import")
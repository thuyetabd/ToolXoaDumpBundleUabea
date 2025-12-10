import json
import sys
import os

# --- CẤU HÌNH ---
INPUT_FILE = 'data.json'          
OUTPUT_FILE = 'new_data.json'      
EXPORT_TXT = 'source_english.txt' 
IMPORT_TXT = 'translated.txt'     
LANG_INDEX = 0  # 0 là tiếng Anh (dòng đầu tiên trong Array)

# --- HÀM DUYỆT ĐỆ QUY THÔNG MINH ---
def traverse_json(node, operation, context, path=""):
    """
    node: Dữ liệu hiện tại
    operation: 'export' hoặc 'import'
    context: Biến lưu trữ chung
    path: Đường dẫn hiện tại (để debug lỗi)
    """
    
    # 1. Nếu là Dictionary (Object {})
    if isinstance(node, dict):
        
        # --- BỘ DÒ TÌM TEXT ARRAY ---
        target_array = None
        found_type = ""

        # Trường hợp 1: Game cũ (Unity Localization Package)
        if 'texts' in node and isinstance(node['texts'], dict) and 'Array' in node['texts']:
            target_array = node['texts']['Array']
            found_type = "texts"
            
        # Trường hợp 2: Game mới (I2 Localization)
        elif 'Languages' in node and isinstance(node['Languages'], dict) and 'Array' in node['Languages']:
            target_array = node['Languages']['Array']
            found_type = "Languages"

        # --- XỬ LÝ NẾU TÌM THẤY ---
        if target_array is not None and isinstance(target_array, list):
            # Kiểm tra xem có đủ ngôn ngữ không
            if len(target_array) > LANG_INDEX:
                
                # --- EXPORT ---
                if operation == 'export':
                    raw_text = target_array[LANG_INDEX]
                    if raw_text is None: raw_text = ""
                    
                    # --- SỬA LỖI: Xử lý cả \r và \n để đảm bảo 1 dòng duy nhất ---
                    # Thay thế \r trước, sau đó mới thay thế \n
                    safe_text = raw_text.replace('\r', '\\r').replace('\n', '\\n')
                    
                    context['lines'].append(safe_text)
                    
                # --- IMPORT ---
                elif operation == 'import':
                    current_idx = context['counter']
                    translated_lines = context['lines']
                    
                    if current_idx < len(translated_lines):
                        line_content = translated_lines[current_idx]
                        
                        # --- SỬA LỖI: Đổi ngược cả \n và \r về nguyên gốc ---
                        final_text = line_content.replace('\\n', '\n').replace('\\r', '\r')
                        
                        target_array[LANG_INDEX] = final_text
                        context['counter'] += 1
                    else:
                        if not context['error_shown']:
                            print(f"\n[LỖI] File dịch hết dòng tại vị trí JSON: {path}")
                            print(f"Nội dung gốc tại đây là: {target_array[LANG_INDEX]}")
                            context['error_shown'] = True
            
            # Đã xử lý xong node này, không cần đào sâu vào children của nó nữa
            return

        # Nếu không phải node chứa text, tiếp tục đào sâu vào các con của nó
        for key, value in node.items():
            traverse_json(value, operation, context, path + f"['{key}']")

    # 2. Nếu là List (Array [])
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
    print("Đang quét và xuất dữ liệu...")
    traverse_json(data, 'export', context)

    if len(context['lines']) == 0:
        print("CẢNH BÁO: Không tìm thấy dòng text nào! Kiểm tra lại cấu trúc JSON.")
    else:
        with open(EXPORT_TXT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(context['lines']))
        
        print(f"-> Đã xuất {len(context['lines'])} dòng ra '{EXPORT_TXT}'.")
        print("LƯU Ý: Các chỗ xuống dòng đã được chuyển thành '\\n' và '\\r'.")

# --- NHẬP ---
def import_text():
    if not os.path.exists(IMPORT_TXT):
        print(f"Lỗi: Không tìm thấy file '{IMPORT_TXT}'")
        return

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file gốc {INPUT_FILE}")
        return
    
    with open(IMPORT_TXT, 'r', encoding='utf-8') as f:
        # Đọc file và loại bỏ ký tự xuống dòng thừa ở cuối dòng
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
            print(f"   -> Dư {txt_lines - json_slots} dòng trong file Text chưa được dùng.")
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

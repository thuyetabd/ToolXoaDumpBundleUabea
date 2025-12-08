import os
import re
import json
import sys

def get_files_in_folder(folder_path, extension=".txt"):
    """Lấy danh sách file trong thư mục"""
    return [f for f in os.listdir(folder_path) if f.endswith(extension)]

def extract_text(input_dir, output_dir):
    """Gom text từ nhiều file dump vào 1 file JSON"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"-> Đã tạo thư mục mới: {output_dir}")

    files = get_files_in_folder(input_dir)
    if not files:
        print(f"Lỗi: Không tìm thấy file .txt nào trong {input_dir}")
        return

    all_data = {}

    print(f"Đang quét {len(files)} file...")
    
    for filename in files:
        file_path = os.path.join(input_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tìm tất cả dòng m_Localized
        matches = re.findall(r'm_Localized = "(.*?)"', content)
        
        # Chỉ lưu file nào có text để dịch
        if matches:
            all_data[filename] = matches

    # Xuất ra file JSON
    json_path = os.path.join(output_dir, "dich_tai_day.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    print("-" * 30)
    print(f"THÀNH CÔNG! Đã xuất {len(all_data)} file chứa text.")
    print(f"File cần dịch nằm tại: {json_path}")

def import_text(original_dump_dir, json_dir):
    """Đọc JSON đã dịch và tạo lại file dump"""
    json_path = os.path.join(json_dir, "dich_tai_day.json")
    
    if not os.path.exists(json_path):
        print(f"Lỗi: Không tìm thấy file 'dich_tai_day.json' trong {json_dir}")
        return

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            translated_data = json.load(f)
    except json.JSONDecodeError:
        print("Lỗi: File JSON bị lỗi cú pháp. Kiểm tra lại dấu phẩy hoặc ngoặc kép.")
        return

    print(f"Đang xử lý nhập liệu cho {len(translated_data)} file...")

    for filename, trans_lines in translated_data.items():
        original_path = os.path.join(original_dump_dir, filename)
        
        # Kiểm tra xem file gốc có còn đó không để làm mẫu
        if not os.path.exists(original_path):
            print(f"Cảnh báo: Không tìm thấy file gốc {filename}, bỏ qua.")
            continue

        with open(original_path, 'r', encoding='utf-8') as f:
            dump_lines = f.readlines()

        new_content = []
        idx = 0
        
        # Duyệt từng dòng file gốc và thay thế bằng text trong JSON
        for line in dump_lines:
            if 'm_Localized =' in line:
                part1 = line.split('"')[0]
                if idx < len(trans_lines):
                    # Lấy text từ JSON đắp vào
                    new_text = trans_lines[idx]
                    new_line = f'{part1}"{new_text}"\n'
                    idx += 1
                else:
                    new_line = line # Hết dịch thì giữ nguyên
                new_content.append(new_line)
            else:
                new_content.append(line)

        # Xuất file mới vào cùng thư mục với file JSON (Folder 2)
        output_file_path = os.path.join(json_dir, filename)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_content)
            
    print("-" * 30)
    print("THÀNH CÔNG! Các file dump mới đã được tạo tại thư mục chứa file JSON.")
    print("Bạn có thể Import chúng trở lại bằng UABE.")

def main():
    print("TOOL DỊCH UABE DUMP TỰ ĐỘNG")
    print("1. Gom text (Folder Gốc -> Ra 1 file JSON)")
    print("2. Trả text (File JSON -> Ra các file Dump mới)")
    mode = input("Chọn chế độ (1 hoặc 2): ")

    if mode == '1':
        folder_goc = input("Nhập đường dẫn thư mục chứa file Dump gốc (Folder 1): ").strip('"')
        folder_dich = input("Nhập đường dẫn thư mục muốn lưu file dịch (Folder 2): ").strip('"')
        extract_text(folder_goc, folder_dich)
    
    elif mode == '2':
        folder_goc = input("Nhập đường dẫn thư mục chứa file Dump gốc để tham chiếu (Folder 1): ").strip('"')
        folder_dich = input("Nhập đường dẫn thư mục chứa file JSON đã dịch (Folder 2): ").strip('"')
        import_text(folder_goc, folder_dich)
    else:
        print("Vui lòng chỉ nhập 1 hoặc 2.")
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
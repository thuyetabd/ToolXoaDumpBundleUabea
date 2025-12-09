import os
import csv
import re

# --- CẤU HÌNH CỐ ĐỊNH (Không cần sửa) ---
DATA_FOLDER = "Tool_Data"           # Thư mục chứa file trung gian
OUT_FOLDER  = "Tool_Output"         # Thư mục chứa file thành phẩm
FILE_REF    = "map_reference.csv"   # File ghi nhớ cấu trúc
FILE_GOC    = "ngonngugoc.txt"      # File chứa text gốc
FILE_DICH   = "ngonngudich.txt"     # File để paste bản dịch vào

# Regex Unity
RE_ID        = re.compile(r'm_Id\s*=\s*(\d+)')
RE_LOCALIZED = re.compile(r'm_Localized\s*=\s*"(.*)"')

def get_txt_files(path):
    if not os.path.exists(path): return []
    return [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(".txt")]

def main():
    print("=== UNITY LOCALIZATION TOOL (AUTO) ===")
    
    # 1. Nhập đường dẫn (Mặc định là thư mục hiện tại)
    print("Nhập đường dẫn thư mục chứa file DUMP (.txt).")
    root_dir = input(">> (Ấn Enter nếu file nằm ngay cạnh tool): ").strip()
    if root_dir == "": 
        root_dir = "." # Thư mục hiện tại

    # Kiểm tra file input
    files = get_txt_files(root_dir)
    if not files:
        print(f"[LỖI] Không tìm thấy file .txt nào trong: {os.path.abspath(root_dir)}")
        input("Ấn Enter để thoát...")
        return

    # 2. Chọn chế độ
    print("\nChọn chế độ:")
    print("1. TRÍCH XUẤT (Tạo file ngonngugoc.txt và ngonngudich.txt)")
    print("2. NẠP LẠI (Đọc file ngonngudich.txt và tạo file mới)")
    mode = input(">> Chọn (1/2): ").strip()

    # Tạo đường dẫn nội bộ
    path_data_dir = os.path.join(root_dir, DATA_FOLDER)
    if not os.path.exists(path_data_dir): os.makedirs(path_data_dir)

    path_ref = os.path.join(path_data_dir, FILE_REF)
    path_goc = os.path.join(path_data_dir, FILE_GOC)
    path_dich = os.path.join(path_data_dir, FILE_DICH)

    # --- CHẾ ĐỘ 1: TRÍCH XUẤT ---
    if mode == "1":
        count = 0
        with open(path_ref, "w", encoding="utf-8", newline="") as f_ref, \
             open(path_goc, "w", encoding="utf-8") as f_goc:
            
            writer = csv.writer(f_ref)
            writer.writerow(["filename", "id"]) # Header

            for file_path in files:
                filename = os.path.basename(file_path)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    current_id = None
                    for line in f:
                        # Tìm ID
                        m_id = RE_ID.search(line)
                        if m_id: current_id = m_id.group(1)
                        
                        # Tìm Text
                        if current_id:
                            m_loc = RE_LOCALIZED.search(line)
                            if m_loc:
                                text = m_loc.group(1)
                                writer.writerow([filename, current_id])
                                f_goc.write(text + "\n")
                                count += 1
                                current_id = None
        
        # Tạo file dịch trống nếu chưa có
        if not os.path.exists(path_dich):
            with open(path_dich, "w", encoding="utf-8") as f: pass

        print(f"\n[XONG] Đã trích xuất {count} dòng.")
        print(f"1. Mở file: {path_goc} -> Copy toàn bộ -> Dịch ở Google.")
        print(f"2. Paste kết quả vào file: {path_dich}")
        print(f"3. Lưu file lại và chạy lại tool chọn chế độ 2.")
        print(f"(Thư mục chứa file: {path_data_dir})")

    # --- CHẾ ĐỘ 2: NẠP LẠI (PACK) ---
    elif mode == "2":
        # Kiểm tra file dịch
        if not os.path.exists(path_dich) or os.path.getsize(path_dich) == 0:
            print(f"[LỖI] File '{FILE_DICH}' không tồn tại hoặc đang TRỐNG!")
            print("Hãy paste nội dung đã dịch vào đó và Lưu lại.")
            return

        # Đọc dữ liệu map
        if not os.path.exists(path_ref):
            print("[LỖI] Thiếu file map reference. Hãy chạy bước 1 trước.")
            return

        with open(path_ref, "r", encoding="utf-8") as f:
            map_data = list(csv.reader(f))[1:] # Bỏ header
        
        with open(path_dich, "r", encoding="utf-8") as f:
            trans_lines = [line.strip('\n') for line in f]

        # Kiểm tra khớp dòng
        if len(map_data) != len(trans_lines):
            print(f"[CẢNH BÁO] Số dòng không khớp! (Gốc: {len(map_data)} vs Dịch: {len(trans_lines)})")
            print("Kết quả có thể bị lệch. Đang tiếp tục...")

        # Tạo dict map nhanh
        trans_map = {}
        for i, (fname, fid) in enumerate(map_data):
            if i < len(trans_lines):
                if fname not in trans_map: trans_map[fname] = {}
                trans_map[fname][fid] = trans_lines[i]

        # Tạo thư mục output
        path_out_dir = os.path.join(root_dir, OUT_FOLDER)
        if not os.path.exists(path_out_dir): os.makedirs(path_out_dir)

        print("Đang xử lý nạp lại...")
        for file_path in files:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(path_out_dir, filename)
            
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            
            with open(dest_path, "w", encoding="utf-8", newline="\n") as f:
                current_id = None
                for line in lines:
                    # Logic tìm và thay thế
                    m_id = RE_ID.search(line)
                    if m_id: current_id = m_id.group(1)
                    
                    if current_id:
                        m_loc = RE_LOCALIZED.search(line)
                        if m_loc:
                            if filename in trans_map and current_id in trans_map[filename]:
                                new_txt = trans_map[filename][current_id]
                                new_txt = new_txt.replace('"', r'\"') # Xử lý dấu ngoặc kép
                                line = f'    1 string m_Localized = "{new_txt}"\n'
                            current_id = None
                    f.write(line)

        print(f"\n[THÀNH CÔNG] File đã tạo xong tại thư mục: {OUT_FOLDER}")
        print(f"Đường dẫn: {os.path.abspath(path_out_dir)}")

    else:
        print("Lựa chọn không hợp lệ.")

    input("\nẤn Enter để kết thúc.")

if __name__ == "__main__":
    main()

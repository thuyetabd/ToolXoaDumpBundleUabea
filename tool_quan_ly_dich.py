import json
import os

# Tên các file
FILE_GOC = 'data.json'          # File gốc của bạn (chứa nội dung trên)
FILE_DICH = 'translate.json'    # File xuất ra để bạn dịch
FILE_KQ = 'data_new.json'       # File kết quả sau khi nén lại

def trich_xuat():
    try:
        with open(FILE_GOC, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Tạo dict đơn giản: ID -> Nội dung
        danh_sach_can_dich = {}
        items = data.get("m_TableData", {}).get("Array", [])
        
        for item in items:
            # Lấy ID và text
            item_id = str(item.get("m_Id"))
            text = item.get("m_Localized")
            danh_sach_can_dich[item_id] = text

        # Lưu ra file mới dễ nhìn hơn để dịch
        with open(FILE_DICH, 'w', encoding='utf-8') as f:
            json.dump(danh_sach_can_dich, f, indent=4, ensure_ascii=False)
        
        print(f"[-] Đã tách text ra file '{FILE_DICH}'. Hãy mở lên và dịch nhé.")
    
    except Exception as e:
        print(f"Lỗi khi tách: {e}")

def nen_lai():
    try:
        # Đọc file gốc để lấy khung sườn
        with open(FILE_GOC, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Đọc file bạn đã dịch
        with open(FILE_DICH, 'r', encoding='utf-8') as f:
            ban_dich = json.load(f)
            
        # Thay thế nội dung cũ bằng nội dung dịch
        items = data.get("m_TableData", {}).get("Array", [])
        count = 0
        for item in items:
            item_id = str(item.get("m_Id"))
            if item_id in ban_dich:
                item["m_Localized"] = ban_dich[item_id]
                count += 1
                
        # Lưu ra file mới
        with open(FILE_KQ, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"[-] Đã nén xong {count} dòng vào file '{FILE_KQ}'.")

    except Exception as e:
        print(f"Lỗi khi nén: {e}")

# Menu chọn
print("Tool dịch Game JSON")
print("1. Tách text ra để dịch")
print("2. Nén text đã dịch vào lại")
chon = input("Chọn số (1 hoặc 2): ")

if chon == '1':
    trich_xuat()
elif chon == '2':
    nen_lai()
else:
    print("Chọn sai rồi.")

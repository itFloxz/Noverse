import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from .main_line import read_line
from .note import note_image
from django.conf import settings
import os
g_clef = {
    'classic': ['ด3', 'ท2', 'ล2', 'ซ2', 'ฟ2', 'ม2', 'ร2', 'ด2', 'ท1', 'ล1', 'ซ1', 'ฟ1', 'ม1', 'ร1', 'ด1'],
    'sharp_1': ['ด3', 'ท2', 'ล2', 'ซ2', 'ฟ#2', 'ม2', 'ร2', 'ด2', 'ท1', 'ล1', 'ซ1', 'ฟ#1', 'ม1', 'ร1', 'ด1'],
    'sharp_2': ['ด#3', 'ท2', 'ล2', 'ซ2', 'ฟ#2', 'ม2', 'ร2', 'ด#2', 'ท1', 'ล1', 'ซ1', 'ฟ#1', 'ม1', 'ร1', 'ด#1'],
    'sharp_3': ['ด#3', 'ท2', 'ล#2', 'ซ2', 'ฟ#2', 'ม2', 'ร2', 'ด#2', 'ท1', 'ล#1', 'ซ1', 'ฟ#1', 'ม1', 'ร1', 'ด#1'],
    'sharp_4': ['ด#3', 'ท2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม2', 'ร2', 'ด#2', 'ท1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม1', 'ร1', 'ด#1'],
    'sharp_5': ['ด#3', 'ท2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม2', 'ร#2', 'ด#2', 'ท1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม1', 'ร#1', 'ด#1'],
    'sharp_6': ['ด#3', 'ท2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม#2', 'ร#2', 'ด#2', 'ท1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม#1', 'ร#1', 'ด#1'],
    'sharp_7': ['ด#3', 'ท#2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม#2', 'ร#2', 'ด#2', 'ท#1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม#1', 'ร#1', 'ด#1'],
    'flat_1': ['ด3', 'ทb2', 'ล2', 'ซ2', 'ฟ2', 'ม2', 'ร2', 'ด2', 'ทb1', 'ล1', 'ซ1', 'ฟ1', 'ม1', 'ร1', 'ด1'],
    'flat_2': ['ด3', 'ทb2', 'ล2', 'ซ2', 'ฟ2', 'มb2', 'ร2', 'ด2', 'ทb1', 'ล1', 'ซ1', 'ฟ1', 'มb1', 'ร1', 'ด1'],
    'flat_3': ['ด3', 'ทb2', 'ลb2', 'ซ2', 'ฟ2', 'มb2', 'ร2', 'ด2', 'ทb1', 'ลb1', 'ซ1', 'ฟ1', 'มb1', 'ร1', 'ด1'],
    'flat_4': ['ด3', 'ทb2', 'ลb2', 'ซ2', 'ฟ2', 'มb2', 'รb2', 'ด2', 'ทb1', 'ลb1', 'ซ1', 'ฟ1', 'มb1', 'รb1', 'ด1'],
    'flat_5': ['ด3', 'ทb2', 'ลb2', 'ซb2', 'ฟ2', 'มb2', 'รb2', 'ด2', 'ทb1', 'ลb1', 'ซb1', 'ฟ1', 'มb1', 'รb1', 'ด1'],
    'flat_6': ['ดb3', 'ทb2', 'ลb2', 'ซb2', 'ฟ2', 'มb2', 'รb2', 'ดb2', 'ทb1', 'ลb1', 'ซb1', 'ฟ1', 'มb1', 'รb1', 'ดb1'],
    'flat_7': ['ดb3', 'ทb2', 'ลb2', 'ซb2', 'ฟb2', 'มb2', 'รb2', 'ดb2', 'ทb1', 'ลb1', 'ซb1', 'ฟb1', 'มb1', 'รb1', 'ดb1']
}
f_clef ={
    'classic': ['ม3', 'ร2', 'ด2', 'ท2', 'ล2', 'ซ2', 'ฟ2', 'ม2', 'ร1', 'ด1', 'ท1', 'ล1', 'ซ1', 'ฟ1', 'ม1'],
    'sharp_1': ['ม3', 'ร2', 'ด2', 'ท2', 'ล2', 'ซ2', 'ฟ#2', 'ม2', 'ร1', 'ด1', 'ท1', 'ล1', 'ซ1', 'ฟ#1', 'ม1'],
    'sharp_2': ['ม3', 'ร2', 'ด#2', 'ท2', 'ล2', 'ซ2', 'ฟ#2', 'ม2', 'ร1', 'ด#1', 'ท1', 'ล1', 'ซ1', 'ฟ#1', 'ม1'],
    'sharp_3': ['ม3', 'ร2', 'ด#2', 'ท2', 'ล#2', 'ซ2', 'ฟ#2', 'ม2', 'ร1', 'ด#1', 'ท1', 'ล#1', 'ซ1', 'ฟ#1', 'ม1'],
    'sharp_4': ['ม3', 'ร2', 'ด#2', 'ท2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม2', 'ร1', 'ด#1', 'ท1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม1'],
    'sharp_5': ['ม3', 'ร#2', 'ด#2', 'ท2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม2', 'ร#1', 'ด#1', 'ท1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม1'],
    'sharp_6': ['ม#3', 'ร#2', 'ด#2', 'ท2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม#2', 'ร#1', 'ด#1', 'ท1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม#1'],
    'sharp_7': ['ม#3', 'ร#2', 'ด#2', 'ท#2', 'ล#2', 'ซ#2', 'ฟ#2', 'ม#2', 'ร#1', 'ด#1', 'ท#1', 'ล#1', 'ซ#1', 'ฟ#1', 'ม#1'],
    'flat_1': ['ม3', 'ร2', 'ด2', 'ทb2', 'ล2', 'ซ2', 'ฟ2', 'ม2', 'ร1', 'ด1', 'ทb1', 'ล1', 'ซ1', 'ฟ1', 'ม1'],
    'flat_2': ['มb3', 'ร2', 'ด2', 'ทb2', 'ล2', 'ซ2', 'ฟ2', 'มb2', 'ร1', 'ด1', 'ทb1', 'ล1', 'ซ1', 'ฟ1', 'มb1'],
    'flat_3': ['มb3', 'ร2', 'ด2', 'ทb2', 'ลb2', 'ซ2', 'ฟ2', 'มb2', 'ร1', 'ด1', 'ทb1', 'ลb1', 'ซ1', 'ฟ1', 'มb1'],
    'flat_4': ['มb3', 'รb2', 'ด2', 'ทb2', 'ลb2', 'ซ2', 'ฟ2', 'มb2', 'รb1', 'ด1', 'ทb1', 'ลb1', 'ซ1', 'ฟ1', 'มb1'],
    'flat_5': ['มb3', 'รb2', 'ด2', 'ทb2', 'ลb2', 'ซb2', 'ฟ2', 'มb2', 'รb1', 'ด1', 'ทb1', 'ลb1', 'ซb1', 'ฟ1', 'มb1'],
    'flat_6': ['มb3', 'รb2', 'ดb2', 'ทb2', 'ลb2', 'ซb2', 'ฟ2', 'มb2', 'รb1', 'ดb1', 'ทb1', 'ลb1', 'ซb1', 'ฟ1', 'มb1'],
    'flat_7': ['มb3', 'รb2', 'ดb2', 'ทb2', 'ลb2', 'ซb2', 'ฟb2', 'มb2', 'รb1', 'ดb1', 'ทb1', 'ลb1', 'ซb1', 'ฟb1', 'มb1']
}



def sort_lines_by_x(data):
    """จัดเรียงข้อมูลในแต่ละบรรทัดตามค่าแกน x"""
    for line in data.keys():
        data[line]["positions"] = sorted(data[line]["positions"], key=lambda pos: pos["x"])
    return data

def get_note_from_y(y, line_data, clef="classic", clef_music="G"):
    """ตรวจจับโน้ตโดยอิงตามค่า y"""
    if clef_music.lower() == "g":
        note_list = g_clef[clef]
    elif clef_music.lower() == "f":
        note_list = f_clef[clef]
    else:
        return None
    
    num_notes = len(note_list)
    line_min_y = line_data['min_y']
    line_max_y = line_data['max_y']
    
    if line_min_y is not None and line_max_y is not None:
        range_y = (line_max_y - line_min_y) / num_notes
        y_positions = np.linspace(line_min_y, line_max_y, num_notes)

        for idx, base_y in enumerate(y_positions):
            bounds_y = [
                (base_y - (range_y * 2), base_y - range_y),
                (base_y - range_y, base_y + range_y),
                (base_y + range_y, base_y + (range_y * 2))
            ]
            
            for lower_bound_y, upper_bound_y in bounds_y:
                if lower_bound_y <= y < upper_bound_y:
                    return note_list[idx]  
    return None 

def assign_notes_to_positions(lines_info, clef="classic", clef_music="G"):
    """วนลูปผ่านทุก line ใน lines_info และดึงข้อมูล y เพื่อค้นหาโน้ต"""
    for line_name, line_data in lines_info.items():
        for position in line_data['positions']:
            y = position['y']
            note = get_note_from_y(y, line_data, clef, clef_music)
            position['note_y'] = note if note else "No match"
    return lines_info

def transform_label(label, note_y):
    """แปลงค่าตัวอักษร label ตามเงื่อนไขและเพิ่ม note_y เข้าไป"""
    if label == "black":
        return f"{note_y}-"
    elif label == "white":
        return f"{note_y}----"
    elif label in ["Eight", "Eight2", "Eight3", "Eight4"]:
        return note_y
    elif label == "white_point":
        return f"{note_y}-----"
    elif label == "black_point":
        return f"{note_y}--"
    else:
        return label  # คืนค่า label เดิมถ้าไม่ตรงเงื่อนไข

def filter_lines_info(lines_info):
    """กรองข้อมูลจาก lines_info เพื่อแสดงเฉพาะ label และ note_y"""
    filtered_info = {}
    
    for line_name, line_data in lines_info.items():
        filtered_positions = [
            {'label': transform_label(position.get('label'), position.get('note_y', "No match"))}
            for position in line_data.get('positions', [])
        ]
        filtered_info[line_name] = filtered_positions
    
    return filtered_info

def extract_all_labels(lines_info):
    """ดึงเฉพาะค่า label จากทุกบรรทัดใน lines_info และรวมเป็นรายการเดียว"""
    all_labels = []
    for positions in lines_info.values():
        all_labels.extend([position['label'] for position in positions])
    return all_labels

def split_label(label):
    """แยกข้อมูลที่มี '-' ออกจากโน้ตหลัก"""
    if '-' in label:
        main_note = label.rstrip('-')  # ตัด '-' ที่ท้ายออกจากโน้ตหลัก
        dashes = '-' * (len(label) - len(main_note))  # นับจำนวน '-' ที่ถูกตัดออก
        return [main_note] + list(dashes)  # แยกเป็น ['โน้ตหลัก', '-', '-', ...]
    else:
        return [label]

def chunk_data(data, chunk_size=4):
    """แบ่งข้อมูลเป็นชิ้นๆ ตามขนาดที่กำหนด"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def format_cell_content(cell_content):
    """ฟอร์แมตเนื้อหาของเซลล์โดยการเชื่อมต่อรายการด้วยช่องว่าง"""
    return ' '.join(cell_content) if isinstance(cell_content, list) else cell_content

def create_pdf(filename, title_text, key, tempo, clef, note_data):
    output_dir = os.path.join(settings.MEDIA_ROOT, 'output')
    os.makedirs(output_dir, exist_ok=True)  
    output_pdf_path = os.path.join(output_dir, filename)
    font_path = r"C:\Users\User\Documents\GitHub\Login\Music-project\django_rest_auth\music_algro\utils\NotoSansThai_Condensed-Bold.ttf"
    pdfmetrics.registerFont(TTFont('NotoSansThai', font_path))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ThaiTitle', fontName='NotoSansThai', fontSize=32, alignment=1))  # Centered title
    styles.add(ParagraphStyle(name='ThaiCell', fontName='NotoSansThai', fontSize=14, alignment=0))  # Left-aligned content
    styles.add(ParagraphStyle(name='ThaiInfo', fontName='NotoSansThai', fontSize=18, alignment=0))  # Left-aligned info
    
    doc = SimpleDocTemplate(output_pdf_path, pagesize=A4)
    elements = []

    title = Paragraph(title_text, styles['ThaiTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5 * cm))
    key_info = Paragraph(f"คีย์เพลง: {key}", styles['ThaiInfo'])
    tempo_info = Paragraph(f"ความเร็ว: {tempo}", styles['ThaiInfo'])
    clef_info = Paragraph(f"กุญแจ: {clef}", styles['ThaiInfo'])
    info_elements = [key_info, Spacer(1, 0.2 * cm), tempo_info, Spacer(1, 0.2 * cm), clef_info]
    elements.extend(info_elements)
    elements.append(Spacer(1, 1 * cm))

    formatted_lines = []
    for row in note_data:
        row_text = format_cell_content(row)
        formatted_lines.append(row_text)

    combined_text = ' | '.join(formatted_lines)
    line_groups = [combined_text[i:i+150] for i in range(0, len(combined_text), 150)]

    for group in line_groups:
        row_paragraph = Paragraph(group, styles['ThaiCell'])
        elements.append(row_paragraph)
        elements.append(Spacer(1, 0.3 * cm))

    doc.build(elements)
    print(f"PDF สร้างเสร็จเรียบร้อยที่ {output_pdf_path}")

def process_music_sheet(image_path, output_pdf_path="song_structure_custom.pdf", title_text="เพลง บรรเลงใจ", key="C Major", tempo="120 BPM", clef_type="classic", clef_music="G"):
    """
    ฟังก์ชันหลักในการประมวลผลแผ่นโน้ตและสร้าง PDF
    
    :param image_path: เส้นทางไปยังรูปภาพแผ่นโน้ต
    :param output_pdf_path: ชื่อไฟล์ PDF ที่จะสร้าง
    :param title_text: ข้อความหัวเรื่องใน PDF
    :param key: คีย์เพลง
    :param tempo: ความเร็วของเพลง
    :param clef_type: ประเภทของกุญแจ (classic, sharp_1, flat_1, ฯลฯ)
    :param clef_music: ประเภทของกุญแจดนตรี ("G" หรือ "F")
    """
    lines_info, total_labels, max_x_coordinates = note_image(image_path)
    lines_info = sort_lines_by_x(lines_info)
    print(f"\nTotal Labels: {total_labels} and {lines_info} and {max_x_coordinates}")
    
    lines_info = assign_notes_to_positions(lines_info, clef=clef_type, clef_music=clef_music)
    
    filtered_lines_info = filter_lines_info(lines_info)
    
    all_labels = extract_all_labels(filtered_lines_info)
    
    split_labels = [item for label in all_labels if label != 'No match' for item in split_label(label)]
    
    table_data = chunk_data(split_labels)
    
    create_pdf(
        filename=output_pdf_path,
        title_text=title_text,
        key=key,
        tempo=tempo,
        clef=clef_music,
        note_data=table_data
    )
    
    print(table_data)

# ตัวอย่างการเรียกใช้ฟังก์ชัน
# if __name__ == "__main__":
#     image_path = r"D:\BACKUP 06-08-2024\Desktop\project-1\image2.png"
#     output_pdf_path = "song_structure_custom.pdf"
#     process_music_sheet(
#         image_path=image_path,
#         output_pdf_path=output_pdf_path,
#         title_text="เพลง บรรเลงใจ",
#         key="C Major",
#         tempo="120 BPM",
#         clef_type="classic",  # เปลี่ยนเป็น 'sharp_1', 'flat_1', ฯลฯ ตามต้องการ
#         clef_music="G"  # หรือ "F"
#     )

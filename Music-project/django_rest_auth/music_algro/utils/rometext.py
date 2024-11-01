import cv2

def remove_text(input_path, resize_dim=(1080, 1000), area_range=(0, 30000)):
    """
    ประมวลผลภาพเพื่อลบข้อความจากภาพและส่งภาพที่ประมวลผลแล้วกลับมา

    Parameters:
    - input_path (str): เส้นทางไปยังภาพต้นฉบับ
    - resize_dim (tuple): ขนาดการปรับขนาดของภาพเอาต์พุต ค่าเริ่มต้นคือ (1080, 1000)
    - area_range (tuple): ช่วงพื้นที่ขั้นต่ำและสูงสุดสำหรับการกรองคอนทัวร์ ค่าเริ่มต้นคือ (350, 16000)

    Returns:
    - image (ndarray): ภาพที่ประมวลผลแล้ว
    """
    # อ่านภาพต้นฉบับ
    image = cv2.imread(input_path)

    if image is None:
        print(f"Error: ไม่สามารถอ่านภาพจาก {input_path}")
        return None

    # แปลงเป็นภาพสีเทา
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ใช้การ thresholding
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # ทำการปิดรูปร่างเชิงมอร์ฟ
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, close_kernel, iterations=1)
    dilate = cv2.dilate(close, dilate_kernel, iterations=2)

    # หาเส้นขอบคอนทัวร์
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # วนลูปไปตามคอนทัวร์และวาดกรอบสี่เหลี่ยมบนภาพต้นฉบับ
    for c in cnts:
        area = cv2.contourArea(c)
        if area > area_range[0] and area < area_range[1]:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)

    # ปรับขนาดภาพ
    # resized_image = cv2.resize(image, resize_dim)

    # ส่งค่าภาพที่ประมวลผลแล้วกลับมา
    return image
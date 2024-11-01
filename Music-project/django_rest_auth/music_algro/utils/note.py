from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
from .main_line import read_line  


def merge_overlapping_bboxes(bboxes):
    """
    รวมกรอบสี่เหลี่ยมที่ทับกันเข้าด้วยกัน
    bboxes: list ของ tuples (x, y, w, h)
    คืนค่ากรอบสี่เหลี่ยมที่ถูกรวมแล้ว
    """
    if not bboxes:
        return []

    # แปลงเป็นรายการของรายการสำหรับความสามารถในการแก้ไข
    bboxes = [list(bbox) for bbox in bboxes]
    merged = True
    while merged:
        merged = False
        for i in range(len(bboxes)):
            for j in range(i + 1, len(bboxes)):
                bbox1 = bboxes[i]
                bbox2 = bboxes[j]
                # ตรวจสอบว่ากรอบสองกรอบทับกันหรือไม่
                if not (bbox1[0] + bbox1[2] < bbox2[0] or bbox2[0] + bbox2[2] < bbox1[0] or
                        bbox1[1] + bbox1[3] < bbox2[1] or bbox2[1] + bbox2[3] < bbox1[1]):
                    # รวมกรอบเข้าด้วยกัน
                    new_x = min(bbox1[0], bbox2[0])
                    new_y = min(bbox1[1], bbox2[1])
                    new_w = max(bbox1[0] + bbox1[2], bbox2[0] + bbox2[2]) - new_x
                    new_h = max(bbox1[1] + bbox1[3], bbox2[1] + bbox2[3]) - new_y
                    bboxes[i] = [new_x, new_y, new_w, new_h]
                    del bboxes[j]
                    merged = True
                    break
            if merged:
                break
    return [tuple(bbox) for bbox in bboxes]

def note_image(image_path):
    """
    ประมวลผลภาพและจัดกลุ่มตำแหน่งลงในบรรทัดต่าง ๆ
    image_path: เส้นทางของไฟล์ภาพ
    คืนค่า:
        lines: dictionary ของบรรทัดต่าง ๆ พร้อมกับข้อมูล labels และ positions
        total_labels: จำนวนรวมของ labels ทั้งหมด
    """
    # เปิดภาพ
    if isinstance(image_path, np.ndarray):
        image = Image.fromarray(image_path)
    else:
        image = Image.open(image_path)
    
    modified_image, grouped_max_y_coordinates_array, max_x_coordinates, start_y_coords = read_line(image)

    # แปลงภาพเป็นโหมด RGB
    image = image.convert("RGB")

    # รับขนาดของภาพ
    width, height = image.size

    # กำหนดค่า threshold
    threshold = 128

    # โหลดข้อมูลพิกเซล
    pixels = image.load()

    # ขั้นตอนที่ 1: แปลงภาพเป็นสีดำและขาว (ไบนารี)
    for y in range(height):
        black_pixel_count = 0
        for x in range(width):
            # รับค่า RGB ของพิกเซล
            red, green, blue = pixels[x, y]

            # คำนวณค่าเกรย์สเกล
            gray = (red + green + blue) // 3

            # กำหนดค่าไบนารีตาม threshold
            binary_value = 255 if gray >= threshold else 0

            # อัปเดตค่าพิกเซลเป็นไบนารี (ขาวหรือดำ)
            pixels[x, y] = (binary_value, binary_value, binary_value)

            # นับจำนวนพิกเซลดำในแถว
            if binary_value == 0:
                black_pixel_count += 1

        # ขั้นตอนที่ 2: ลบเส้นแนวนอน
        if (black_pixel_count * 100 / width) > 28:  # ถ้ามากกว่า 28% ของแถวเป็นสีดำ
            for x in range(width):
                # ตั้งค่าแถวทั้งหมดเป็นสีขาว
                pixels[x, y] = (255, 255, 255)

    # ขั้นตอนที่ 3: แปลงกลับเป็น numpy array
    image_np = np.array(image)

    # แปลงภาพเป็นไบนารี (0 และ 255)
    binary_image = (image_np[:, :, 0] == 0).astype(np.uint8) * 255

    # ขั้นตอนที่ 4: การขยายเชิงมอร์โฟโลยี
    kernel = np.ones((3, 3), np.uint8)  # สร้าง kernel 3x3
    dilated_image = cv2.dilate(binary_image, kernel, iterations=1)

    # ขั้นตอนที่ 5: ลบพื้นที่สีดำขนาดเล็ก (น้อยกว่า 3 พิกเซล)
    # ใช้ erosion เพื่อลบ noise ขนาดเล็ก
    eroded_image = cv2.erode(dilated_image, kernel, iterations=1)
    dilated_image_cleaned = cv2.dilate(eroded_image, kernel, iterations=1)

    # ขั้นตอนที่ 6: สร้างสำเนาของภาพต้นฉบับสำหรับกรอบขนาดใหญ่และขนาดเล็ก
    large_box_image = image.copy()  # สำเนาสำหรับกรอบขนาดใหญ่
    small_box_image = image.copy()  # สำเนาสำหรับกรอบขนาดเล็ก

    # แปลงเป็น numpy arrays สำหรับการวาด
    large_box_image_np = np.array(large_box_image)
    small_box_image_np = np.array(small_box_image)

    # ขั้นตอนที่ 7: ตรวจจับพื้นที่สีดำ (คอนทัวร์) ในภาพ
    contours, _ = cv2.findContours(dilated_image_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # ขั้นตอนที่ 8: รวมคอนทัวร์ที่อยู่ใกล้กันและตรวจสอบการทับซ้อน
    merged_boxes = merge_overlapping_bboxes([cv2.boundingRect(contour) for contour in contours])

    # ขั้นตอนที่ 9: วาดกรอบสี่เหลี่ยมตามพื้นที่กล่อง
    total_black_area_large = 0
    total_black_area_small = 0

    # กำหนดค่า threshold_y จาก grouped_max_y_coordinates_array
    # สมมติว่า grouped_max_y_coordinates_array เป็น list of lists
    if isinstance(grouped_max_y_coordinates_array, np.ndarray):
        grouped_max_y_coordinates = grouped_max_y_coordinates_array.tolist()
    else:
        grouped_max_y_coordinates = grouped_max_y_coordinates_array

    threshold_y = grouped_max_y_coordinates[0][6]
    threshold_x_max = max(max_x_coordinates) + 100
    threshold_x_min = min(max_x_coordinates) + 80

    marked_positions = []

    for box_index, (x, y, w, h) in enumerate(merged_boxes, start=1):
        # ตรวจสอบเงื่อนไขเพิ่มเติมก่อนประมวลผลกรอบสี่เหลี่ยม
        if (y < threshold_y and x < threshold_x_max) or (y > threshold_y and x < threshold_x_min):
            dilated_image_cleaned[y:y+h, x:x+w] = 255
            binary_image[y:y+h, x:x+w] = 255
            large_box_image_np[y:y+h, x:x+w] = [255, 255, 255]
            small_box_image_np[y:y+h, x:x+w] = [255, 255, 255]
            image_np[y:y+h, x:x+w] = [255, 255, 255]
            continue

        # คำนวณพื้นที่ของกรอบสี่เหลี่ยม
        box_area = w * h

        # นับพิกเซลดำภายในกรอบสี่เหลี่ยม
        black_pixels_in_box = np.sum(dilated_image_cleaned[y:y+h, x:x+w] == 255)

        # คำนวณเปอร์เซ็นต์ของพิกเซลดำภายในกรอบสี่เหลี่ยม
        black_percentage = int((black_pixels_in_box / box_area) * 100)

        if 490 <= black_pixels_in_box <= 506:
            # วาดกรอบสี่เหลี่ยมสีแดง
            cv2.rectangle(large_box_image_np, (x, y), (x + w, y + h), (255, 0, 0), 2)  # สี่เหลี่ยมสีแดง

            cv2.putText(large_box_image_np, f"Eight", (x, y + h + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            # === ตรวจสอบว่าพื้นที่สีดำอยู่ด้านบนหรือด้านล่าง ===

            roi = dilated_image_cleaned[y:y+h, x:x+w]

            half_h = h // 2
            top_half = roi[0:half_h, :]
            bottom_half = roi[half_h:, :]

            black_pixels_top = np.sum(top_half == 255)
            black_pixels_bottom = np.sum(bottom_half == 255)

            if black_pixels_top > black_pixels_bottom:
                label = "Top"
            else:
                label = "Bottom"

            cv2.putText(large_box_image_np, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # หาและมาร์คตำแหน่ง
            ys, xs = np.where(roi == 255)

            if len(ys) == 0:
                continue

            if label == 'Top':
                min_y_in_roi = np.min(ys)
                y_position = y + min_y_in_roi + 5
            else:
                max_y_in_roi = np.max(ys)
                y_position = y + max_y_in_roi - 5

            x_position = x + w // 2

            cv2.circle(large_box_image_np, (x_position, int(y_position)), 3, (0, 0, 255), -1)

            marked_positions.append(("Eight", (x_position, int(y_position))))

        elif box_area > 2500 and black_percentage <= 40:
            black_pixels_in_box_half = black_pixels_in_box // 2  # แบ่งจำนวนพิกเซลดำครึ่งหนึ่ง

            # วาดกรอบสี่เหลี่ยมสีแดง
            cv2.rectangle(large_box_image_np, (x, y), (x + w, y + h), (255, 0, 0), 2)  # สี่เหลี่ยมสีแดง

            # แสดงจำนวนพิกเซลดำครึ่งหนึ่งและพื้นที่ของกรอบ
            cv2.putText(large_box_image_np, f"{black_pixels_in_box_half} px", (x, y + h + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            cv2.putText(large_box_image_np, f"{box_area} px", (x, y + h + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            # กำหนดจำนวนส่วนที่จะแบ่งกรอบ
            division_number = 1
            label_text = ""

            if black_pixels_in_box_half > 600:
                black_pixels_in_box_half2 = black_pixels_in_box_half // 2
                if black_pixels_in_box_half2 > 300:
                    division_number = 4  # Eight4
                    label_text = "Eight4"
                else:
                    division_number = 3  # Eight3
                    label_text = "Eight3"
            else:
                division_number = 2  # Eight2
                label_text = "Eight2"

            # แสดงข้อความตาม division_number
            cv2.putText(large_box_image_np, label_text, (x, y + h + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            # คำนวณความกว้างของแต่ละส่วนที่จะแบ่ง
            divided_width = w // division_number

            # วาดกรอบสี่เหลี่ยมสีเขียวภายในกรอบสีแดงและเก็บจำนวนพิกเซลดำในแต่ละส่วน
            black_pixels_in_green_boxes = []
            positions = []  # List สำหรับเก็บตำแหน่งที่มาร์คภายในกรอบขนาดใหญ่

            for i in range(division_number):
                # คำนวณตำแหน่งมุมซ้ายบนของกรอบเล็ก
                top_left_x = x + i * divided_width
                # คำนวณตำแหน่งมุมขวาล่างของกรอบเล็ก
                bottom_right_x = top_left_x + divided_width if i < division_number - 1 else x + w

                # วาดกรอบสี่เหลี่ยมสีเขียวรอบกลุ่ม
                cv2.rectangle(large_box_image_np, 
                              (top_left_x, y), 
                              (bottom_right_x, y + h), 
                              (0, 255, 0), 1)

                # === คำนวณความเข้มของพิกเซลดำในแต่ละส่วน ===

                # ดึง ROI ของกรอบเล็ก
                roi = dilated_image_cleaned[y:y + h, top_left_x:bottom_right_x]

                # นับจำนวนพิกเซลดำใน ROI
                black_pixels_in_roi = np.sum(roi == 255)

                # บันทึกจำนวนพิกเซลดำและตำแหน่งของกรอบเล็ก
                black_pixels_in_green_boxes.append((i, black_pixels_in_roi, top_left_x, bottom_right_x))

            if black_pixels_in_green_boxes:
                # ค้นหากรอบเล็กที่มีพิกเซลดำน้อยที่สุด
                min_black_pixels = min(black_pixels_in_green_boxes, key=lambda x: x[1])

                # ไฮไลท์กรอบเล็กที่มีพิกเซลดำน้อยที่สุดด้วยสีม่วง
                cv2.rectangle(large_box_image_np, (min_black_pixels[2], y), (min_black_pixels[3], y + h), (255, 0, 255), 2)

                # แสดงจำนวนพิกเซลดำในกรอบเล็กที่น้อยที่สุด
                cv2.putText(large_box_image_np, f"Least Black: {min_black_pixels[1]} px",
                            (min_black_pixels[2], y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)

                # === ตรวจสอบว่าพื้นที่สีดำอยู่ด้านบนหรือด้านล่าง ===

                # ดึง ROI ของกรอบสีม่วง
                magenta_roi = dilated_image_cleaned[y:y + h, min_black_pixels[2]:min_black_pixels[3]]

                # แบ่ง ROI เป็นส่วนบนและส่วนล่าง
                half_h = h // 2
                top_half = magenta_roi[0:half_h, :]
                bottom_half = magenta_roi[half_h:, :]

                # นับจำนวนพิกเซลดำในแต่ละส่วน
                black_pixels_top = np.sum(top_half == 255)
                black_pixels_bottom = np.sum(bottom_half == 255)

                # กำหนด label เป็น "Top" หรือ "Bottom" ตามจำนวนพิกเซลดำ
                if black_pixels_top > black_pixels_bottom:
                    label = "Top"
                else:
                    label = "Bottom"

                # แสดง label บนกรอบสีแดง
                cv2.putText(large_box_image_np, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # === หาตำแหน่งและมาร์คบนภาพ ===
                for idx, (i, _, top_left_x, bottom_right_x) in enumerate(black_pixels_in_green_boxes):
                    # ดึง ROI ของกรอบเล็ก
                    roi = dilated_image_cleaned[y:y + h, top_left_x:bottom_right_x]

                    # หา y-coordinates ของพิกเซลดำใน ROI
                    ys, xs = np.where(roi == 255)

                    if len(ys) == 0:
                        # ไม่มีพิกเซลดำในกรอบเล็กนี้
                        continue

                    if label == 'Top':
                        # หา y ที่มีค่าต่ำที่สุด (ใกล้ด้านบน)
                        min_y_in_roi = np.min(ys)
                        y_position = y + min_y_in_roi + 5  # เพิ่มค่า y ขึ้นมา 5
                    else:  # label == 'Bottom'
                        # หา y ที่มีค่ามากที่สุด (ใกล้ด้านล่าง)
                        max_y_in_roi = np.max(ys)
                        y_position = y + max_y_in_roi - 5  # ลดค่า y ลงมา 5

                    # คำนวณตำแหน่ง x เป็นกลางของกรอบเล็ก
                    x_position = (top_left_x + bottom_right_x) // 2

                    # มาร์คตำแหน่งบนภาพด้วยวงกลมสีแดง
                    cv2.circle(large_box_image_np, (x_position, int(y_position)), 3, (0, 0, 255), -1)  # วงกลมสีแดง

                    # เก็บข้อมูลตำแหน่งใน list ของกรอบขนาดใหญ่
                    positions.append((x_position, int(y_position)))

                # เก็บข้อมูลในรูปแบบของอาเรย์ตาม division_number
                if division_number == 2:
                    marked_positions.append(("Eight2", tuple(positions)))
                elif division_number == 3:
                    marked_positions.append(("Eight3", tuple(positions)))
                elif division_number == 4:
                    marked_positions.append(("Eight4", tuple(positions)))

                # รวมจำนวนพิกเซลดำสำหรับกรอบขนาดใหญ่
                total_black_area_large += black_pixels_in_box_half

        elif black_percentage <= 40 and black_pixels_in_box >= 250:
            # วาดกรอบสี่เหลี่ยมสีแดง
            cv2.rectangle(small_box_image_np, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # คำนวณความแตกต่างพื้นที่เป็นเปอร์เซ็นต์
            difference_Area = (black_pixels_in_box / box_area) * 100

            # แสดงจำนวนพิกเซลดำและพื้นที่ของกรอบ
            cv2.putText(small_box_image_np, f"{black_pixels_in_box} px", (x, y + h + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            cv2.putText(small_box_image_np, f"{box_area} px", (x, y + h + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            # แสดงข้อความ "White" หรือ "Black" ตามค่า difference_Area
            if difference_Area <= 25:
                label_text = "White"
            else:
                label_text = "Black"

            cv2.putText(small_box_image_np, label_text, (x, y + h + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

            # === นับจำนวนกลุ่มของพื้นที่สีดำภายในกรอบ ===

            # กำหนดขนาดขั้นต่ำของกลุ่ม
            min_group_size = 10  # พิกเซล

            # ดึง ROI ของกรอบสี่เหลี่ยมจากภาพ dilated_image_cleaned
            roi = dilated_image_cleaned[y:y+h, x:x+w]

            # === ตรวจสอบว่าพื้นที่สีดำในกรอบสีแดงอยู่ด้านบนหรือด้านล่าง ===

            # แบ่งกรอบสีแดงเป็นส่วนบนและส่วนล่าง
            half_h = h // 2
            top_half = roi[0:half_h, :]
            bottom_half = roi[half_h:, :]

            # นับจำนวนพิกเซลดำในแต่ละส่วน
            black_pixels_top = np.sum(top_half == 255)
            black_pixels_bottom = np.sum(bottom_half == 255)

            # กำหนดว่าอยู่ด้านบนหรือด้านล่าง
            if black_pixels_top > black_pixels_bottom:
                position_label = "Top"
                y_position = y + 5  # ขยับ y เพิ่มขึ้น 5
            else:
                position_label = "Bottom"
                y_position = y + h - 5  # ขยับ y ลดลง 5

            # คำนวณตำแหน่ง x เป็นกลางของกรอบสีแดง
            x_position = x + w // 2

            # มาร์คตำแหน่งบนภาพด้วยวงกลมสีแดงใน small_box_image_np
            cv2.circle(small_box_image_np, (x_position, y_position), 3, (0, 0, 255), -1)  # วงกลมสีแดง

            # แสดงตำแหน่งบนกรอบสีแดง
            cv2.putText(small_box_image_np, position_label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # รวมจำนวนพิกเซลดำสำหรับกรอบขนาดเล็ก
            total_black_area_small += black_pixels_in_box

            # === เพิ่มฟังก์ชันการตรวจสอบพื้นที่สีดำขนาดเล็ก (25-40 พิกเซล) ===

            # หาพื้นที่สีดำ (ค่า 255) ภายใน ROI
            # ใช้ connected components เพื่อหากลุ่มพิกเซลที่เชื่อมต่อกัน
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(roi, connectivity=8)

            # ตัวแปรสำหรับเก็บผลรวมของพื้นที่ขนาดเล็ก
            total_small_areas = 0
            point_value = 0
            positions = []  # Reset positions for each box
            for label_comp in range(1, num_labels):  # ข้าม label 0 ซึ่งเป็น background
                area = stats[label_comp, cv2.CC_STAT_AREA]
                if 25 < area <= 40:
                    # รวมพื้นที่เล็กเข้ากับตัวแปรรวม
                    total_small_areas += area

                    # ดึงพิกัดของกลุ่มพิกเซลนั้น
                    x_comp = stats[label_comp, cv2.CC_STAT_LEFT]
                    y_comp = stats[label_comp, cv2.CC_STAT_TOP]
                    w_comp = stats[label_comp, cv2.CC_STAT_WIDTH]
                    h_comp = stats[label_comp, cv2.CC_STAT_HEIGHT]

                    # วาดกรอบสี่เหลี่ยมสีเขียวรอบกลุ่มพิกเซล
                    cv2.rectangle(small_box_image_np, 
                                  (x + x_comp, y + y_comp), 
                                  (x + x_comp + w_comp, y + y_comp + h_comp), 
                                  (0, 255, 0), 1)

                    # คำนวณค่าความแตกต่างระหว่าง black_pixels_in_box และ area เป็นเปอร์เซ็นต์
                    difference = black_pixels_in_box - area
                    default_difference = (difference / box_area) * 100

                    # กำหนดค่า default_difference ตามค่า difference_Area
                    if default_difference <= 25:
                        point_value = 1.0
                    else:
                        point_value = 0.5

                    # แสดงค่าความแตกต่างบนกรอบสีเขียว
                    cv2.putText(small_box_image_np, f"Dif: {default_difference:.2f}", 
                                (x + x_comp, y + y_comp - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
            if label_text == "White" and point_value == 1.0:
                marked_positions.append(("white_point", (x_position, int(y_position))))
            elif label_text == "Black" and point_value == 0.5:
                marked_positions.append(("black_point", (x_position, int(y_position))))
            elif label_text == "White" and point_value == 0:
                marked_positions.append(("white", (x_position, int(y_position))))
            elif label_text == "Black" and point_value == 0:
                marked_positions.append(("black", (x_position, int(y_position))))

    # ขั้นตอนที่ 10: แสดงภาพ
    def display_images(image_np, large_box_image_np, small_box_image_np):
        plt.figure(figsize=(18, 6))

        plt.subplot(1, 3, 1)
        plt.title('Original Image')
        plt.imshow(image_np)
        plt.axis('off')  # ปิดการแสดงแกน

        plt.subplot(1, 3, 2)
        plt.title('Bounding Boxes for Large Areas (> 2500 px)')
        plt.imshow(large_box_image_np)
        plt.axis('off')  # ปิดการแสดงแกน

        plt.subplot(1, 3, 3)
        plt.title('Bounding Boxes for Small Areas (<= 2500 px)')
        plt.imshow(small_box_image_np)
        plt.axis('off')  # ปิดการแสดงแกน

        plt.show()

    # แสดงภาพ
    # display_images(image_np, large_box_image_np, small_box_image_np)

    # บันทึกภาพถ้าต้องการ
    # large_box_output = Image.fromarray(large_box_image_np)
    # small_box_output = Image.fromarray(small_box_image_np)
    
    # Uncomment the lines below to save the images
    # large_box_output.save("large_boxes.png")
    # small_box_output.save("small_boxes.png")

    print("================================", marked_positions)

    # ตรวจสอบว่า grouped_max_y_coordinates_array เป็น list ของ list หรือไม่
    if isinstance(grouped_max_y_coordinates_array, np.ndarray):
        grouped_max_y_coordinates = grouped_max_y_coordinates_array.tolist()
    else:
        grouped_max_y_coordinates = grouped_max_y_coordinates_array

    line_names = [f"Line_{i+1}" for i in range(len(grouped_max_y_coordinates))]

    # แปลงเป็น dict
    grouped_max_y_coordinates_dict = {line_names[i]: y_coords for i, y_coords in enumerate(grouped_max_y_coordinates)}

    # สร้าง dictionary สำหรับบรรทัดพร้อมกับ min_y และ max_y
    lines = {}
    for line_name, y_coords in grouped_max_y_coordinates_dict.items():
        min_y = min(y_coords) - 10
        max_y = max(y_coords) + 10
        lines[line_name] = {'min_y': min_y, 'max_y': max_y, 'positions': []}

    # สร้างกลุ่มสำหรับตำแหน่งที่ไม่ตรงกับบรรทัดใด ๆ
    lines['Unassigned'] = {'min_y': None, 'max_y': None, 'positions': []}

    # ฟังก์ชันเพื่อจัดกลุ่มตำแหน่งลงในบรรทัด
    def assign_positions_to_lines(marked_positions, lines):
        for item in marked_positions:
            label = item[0]
            position = item[1]

            # เพิ่มการดีบัก
            # print(f"Processing label: {label}, position: {position}")

            # ตรวจสอบว่า position เป็น tuple หรือ iterable ของ tuples
            if isinstance(position, tuple) and isinstance(position[0], int):
                # Single position
                positions = [position]
            elif isinstance(position, (list, tuple)) and all(isinstance(pos, tuple) and len(pos) == 2 for pos in position):
                # Multiple positions
                positions = position
            else:
                # print(f"Unexpected position format: {position}")
                continue

            for pos in positions:
                x, y = pos
                assigned = False
                for line_name, line_info in lines.items():
                    if line_name == 'Unassigned':
                        continue
                    if line_info['min_y'] <= y <= line_info['max_y']:
                        # เพิ่มตำแหน่งด้วยคีย์ 'label', 'x', 'y'
                        lines[line_name]['positions'].append({'label': label, 'x': x, 'y': y})
                        print(f"Assigned to {line_name}: label={label}, x={x}, y={y}")
                        assigned = True
                        break
                if not assigned:
                    lines['Unassigned']['positions'].append({'label': label, 'x': x, 'y': y})
                    print(f"Assigned to Unassigned: label={label}, x={x}, y={y}")

    # เรียกใช้ฟังก์ชันเพื่อจัดกลุ่ม
    assign_positions_to_lines(marked_positions, lines)
    # display_images(image_np, large_box_image_np, small_box_image_np)
    # ตรวจสอบว่าแต่ละตำแหน่งมีคีย์ 'label', 'x', 'y' หรือไม่
    # for line_name, line_info in lines.items():
    #     for pos in line_info['positions']:
    #         if 'label' not in pos or 'x' not in pos or 'y' not in pos:
    #             print(f"Missing keys in position: {pos} in {line_name}")

    # เรียงตำแหน่งภายในแต่ละบรรทัดตามค่า x_position จากซ้ายไปขวา
    # for line_name, line_info in lines.items():
    #     line_info['positions'].sort(key=lambda pos: pos['x'])

    # สร้างฟังก์ชันเพื่อรับข้อมูลบรรทัด
    def get_lines_info(lines):
        """
        คืนค่า dictionary ของบรรทัดต่าง ๆ พร้อมกับข้อมูล labels และ positions
        """
        return lines

    # รับข้อมูลบรรทัด
    lines_info = get_lines_info(lines)
    # display_images()

    # แสดงผลลัพธ์พร้อมกับจำนวน labels ต่อบรรทัด
    # for line_name, line_info in lines_info.items():
    #     if line_name != 'Unassigned':
    #         count = len(line_info['positions'])
    #         print(f"\n{line_name} (Y range: {line_info['min_y']} - {line_info['max_y']}): {count} items")
    #         for pos in line_info['positions']:
    #             try:
    #                 print(f"  Label: {pos['label']}, Position: ({pos['x']}, {pos['y']})")
    #             except KeyError as e:
    #                 print(f"  Missing key {e} in position: {pos}")
    #     else:
    #         print(f"\n{line_name}:")
    #         for pos in line_info['positions']:
    #             try:
    #                 print(f"  Label: {pos['label']}, Position: ({pos['x']}, {pos['y']})")
    #             except KeyError as e:
    #                 print(f"  Missing key {e} in position: {pos}")

    # แสดงจำนวน labels ทั้งหมด
    total_labels = sum(len(line_info['positions']) for line_name, line_info in lines_info.items() if line_name != 'Unassigned')
    # print(f"\nTotal Labels: {total_labels}")

    return lines_info, total_labels , grouped_max_y_coordinates_array 

# ตัวอย่างการเรียกใช้งานฟังก์ชัน
# if __name__ == "__main__":
#     image_path = r"D:\BACKUP 06-08-2024\Desktop\project-1\image.png"
#     lines_info, total_labels ,max_x_coordinates= note_image(image_path)
#     print(f"\nTotal Labels: {total_labels} and {lines_info} and {max_x_coordinates}")

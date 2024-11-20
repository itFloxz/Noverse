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
    image = Image.open(image_path)
    modified_image, grouped_max_y_coordinates_array, max_x_coordinates, start_y_coords = read_line(image)
    image = image.convert("RGB")
    width, height = image.size
    threshold = 128
    pixels = image.load()
    for y in range(height):
        black_pixel_count = 0
        for x in range(width):
            red, green, blue = pixels[x, y]
            gray = (red + green + blue) // 3
            binary_value = 255 if gray >= threshold else 0
            pixels[x, y] = (binary_value, binary_value, binary_value)
            if binary_value == 0:
                black_pixel_count += 1

        if (black_pixel_count * 100 / width) > 28: 
            for x in range(width):
                pixels[x, y] = (255, 255, 255)

    image_np = np.array(image)
    binary_image = (image_np[:, :, 0] == 0).astype(np.uint8) * 255
    kernel = np.ones((3, 3), np.uint8) 
    dilated_image = cv2.dilate(binary_image, kernel, iterations=1)
    eroded_image = cv2.erode(dilated_image, kernel, iterations=1)
    dilated_image_cleaned = cv2.dilate(eroded_image, kernel, iterations=1)
    large_box_image = image.copy()  
    small_box_image = image.copy()  
    large_box_image_np = np.array(large_box_image)
    small_box_image_np = np.array(small_box_image)

    contours, _ = cv2.findContours(dilated_image_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    merged_boxes = merge_overlapping_bboxes([cv2.boundingRect(contour) for contour in contours])

    total_black_area_large = 0
    total_black_area_small = 0

    if isinstance(grouped_max_y_coordinates_array, np.ndarray):
        grouped_max_y_coordinates = grouped_max_y_coordinates_array.tolist()
    else:
        grouped_max_y_coordinates = grouped_max_y_coordinates_array

    threshold_y = grouped_max_y_coordinates[0][6]
    threshold_x_max = max(max_x_coordinates) + 100
    threshold_x_min = min(max_x_coordinates) + 80

    marked_positions = []

    for box_index, (x, y, w, h) in enumerate(merged_boxes, start=1):
        if (y < threshold_y and x < threshold_x_max) or (y > threshold_y and x < threshold_x_min):
            dilated_image_cleaned[y:y+h, x:x+w] = 255
            binary_image[y:y+h, x:x+w] = 255
            large_box_image_np[y:y+h, x:x+w] = [255, 255, 255]
            small_box_image_np[y:y+h, x:x+w] = [255, 255, 255]
            image_np[y:y+h, x:x+w] = [255, 255, 255]
            continue
        
        box_area = w * h
        black_pixels_in_box = np.sum(dilated_image_cleaned[y:y+h, x:x+w] == 255)

        black_percentage = int((black_pixels_in_box / box_area) * 100)

        if 490 <= black_pixels_in_box <= 506:
            cv2.rectangle(large_box_image_np, (x, y), (x + w, y + h), (255, 0, 0), 2)  

            cv2.putText(large_box_image_np, f"Eight", (x, y + h + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

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
            black_pixels_in_box_half = black_pixels_in_box // 2  
            cv2.rectangle(large_box_image_np, (x, y), (x + w, y + h), (255, 0, 0), 2) 
            cv2.putText(large_box_image_np, f"{black_pixels_in_box_half} px", (x, y + h + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            cv2.putText(large_box_image_np, f"{box_area} px", (x, y + h + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            division_number = 1
            label_text = ""

            if black_pixels_in_box_half > 600:
                black_pixels_in_box_half2 = black_pixels_in_box_half // 2
                if black_pixels_in_box_half2 > 300:
                    division_number = 4  
                    label_text = "Eight4"
                else:
                    division_number = 3 
                    label_text = "Eight3"
            else:
                division_number = 2  
                label_text = "Eight2"
            cv2.putText(large_box_image_np, label_text, (x, y + h + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            divided_width = w // division_number

            black_pixels_in_green_boxes = []
            positions = []  

            for i in range(division_number):
                top_left_x = x + i * divided_width
                bottom_right_x = top_left_x + divided_width if i < division_number - 1 else x + w
                cv2.rectangle(large_box_image_np, 
                              (top_left_x, y), 
                              (bottom_right_x, y + h), 
                              (0, 255, 0), 1)

                # === คำนวณความเข้มของพิกเซลดำในแต่ละส่วน ===
                roi = dilated_image_cleaned[y:y + h, top_left_x:bottom_right_x]

                black_pixels_in_roi = np.sum(roi == 255)
                black_pixels_in_green_boxes.append((i, black_pixels_in_roi, top_left_x, bottom_right_x))

            if black_pixels_in_green_boxes:
                min_black_pixels = min(black_pixels_in_green_boxes, key=lambda x: x[1])
                cv2.rectangle(large_box_image_np, (min_black_pixels[2], y), (min_black_pixels[3], y + h), (255, 0, 255), 2)
                cv2.putText(large_box_image_np, f"Least Black: {min_black_pixels[1]} px",
                            (min_black_pixels[2], y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)

                # === ตรวจสอบว่าพื้นที่สีดำอยู่ด้านบนหรือด้านล่าง ===
                magenta_roi = dilated_image_cleaned[y:y + h, min_black_pixels[2]:min_black_pixels[3]]
                half_h = h // 2
                top_half = magenta_roi[0:half_h, :]
                bottom_half = magenta_roi[half_h:, :]
                black_pixels_top = np.sum(top_half == 255)
                black_pixels_bottom = np.sum(bottom_half == 255)
                if black_pixels_top > black_pixels_bottom:
                    label = "Top"
                else:
                    label = "Bottom"
                cv2.putText(large_box_image_np, label, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # === หาตำแหน่งและมาร์คบนภาพ ===
                for idx, (i, _, top_left_x, bottom_right_x) in enumerate(black_pixels_in_green_boxes):
                    roi = dilated_image_cleaned[y:y + h, top_left_x:bottom_right_x]
                    ys, xs = np.where(roi == 255)
                    if len(ys) == 0:
                        continue

                    if label == 'Top':
                        min_y_in_roi = np.min(ys)
                        y_position = y + min_y_in_roi + 5  
                    else: 
                        max_y_in_roi = np.max(ys)
                        y_position = y + max_y_in_roi - 5  

                    x_position = (top_left_x + bottom_right_x) // 2
                    cv2.circle(large_box_image_np, (x_position, int(y_position)), 3, (0, 0, 255), -1)  
                    positions.append((x_position, int(y_position)))

                if division_number == 2:
                    marked_positions.append(("Eight2", tuple(positions)))
                elif division_number == 3:
                    marked_positions.append(("Eight3", tuple(positions)))
                elif division_number == 4:
                    marked_positions.append(("Eight4", tuple(positions)))

                total_black_area_large += black_pixels_in_box_half

        elif black_percentage <= 40 and black_pixels_in_box >= 250:
            cv2.rectangle(small_box_image_np, (x, y), (x + w, y + h), (255, 0, 0), 2)
            difference_Area = (black_pixels_in_box / box_area) * 100
            cv2.putText(small_box_image_np, f"{black_pixels_in_box} px", (x, y + h + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
            cv2.putText(small_box_image_np, f"{box_area} px", (x, y + h + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            if difference_Area <= 25:
                label_text = "White"
            else:
                label_text = "Black"

            cv2.putText(small_box_image_np, label_text, (x, y + h + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

            # === นับจำนวนกลุ่มของพื้นที่สีดำภายในกรอบ ===

            min_group_size = 10  
            roi = dilated_image_cleaned[y:y+h, x:x+w]

            # === ตรวจสอบว่าพื้นที่สีดำในกรอบสีแดงอยู่ด้านบนหรือด้านล่าง ===
            half_h = h // 2
            top_half = roi[0:half_h, :]
            bottom_half = roi[half_h:, :]
            black_pixels_top = np.sum(top_half == 255)
            black_pixels_bottom = np.sum(bottom_half == 255)

            if black_pixels_top > black_pixels_bottom:
                position_label = "Top"
                y_position = y + 5  
            else:
                position_label = "Bottom"
                y_position = y + h - 5  
            x_position = x + w // 2

            cv2.circle(small_box_image_np, (x_position, y_position), 3, (0, 0, 255), -1)  

            cv2.putText(small_box_image_np, position_label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            total_black_area_small += black_pixels_in_box

            # === เพิ่มฟังก์ชันการตรวจสอบพื้นที่สีดำขนาดเล็ก (25-40 พิกเซล) ===

            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(roi, connectivity=8)

            total_small_areas = 0
            point_value = 0
            positions = [] 
            for label_comp in range(1, num_labels): 
                area = stats[label_comp, cv2.CC_STAT_AREA]
                if 25 < area <= 40:
                    total_small_areas += area

                    x_comp = stats[label_comp, cv2.CC_STAT_LEFT]
                    y_comp = stats[label_comp, cv2.CC_STAT_TOP]
                    w_comp = stats[label_comp, cv2.CC_STAT_WIDTH]
                    h_comp = stats[label_comp, cv2.CC_STAT_HEIGHT]

                    cv2.rectangle(small_box_image_np, 
                                  (x + x_comp, y + y_comp), 
                                  (x + x_comp + w_comp, y + y_comp + h_comp), 
                                  (0, 255, 0), 1)
                    difference = black_pixels_in_box - area
                    default_difference = (difference / box_area) * 100

                    if default_difference <= 25:
                        point_value = 1.0
                    else:
                        point_value = 0.5

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

    if isinstance(grouped_max_y_coordinates_array, np.ndarray):
        grouped_max_y_coordinates = grouped_max_y_coordinates_array.tolist()
    else:
        grouped_max_y_coordinates = grouped_max_y_coordinates_array

    line_names = [f"Line_{i+1}" for i in range(len(grouped_max_y_coordinates))]
    grouped_max_y_coordinates_dict = {line_names[i]: y_coords for i, y_coords in enumerate(grouped_max_y_coordinates)}

    lines = {}
    for line_name, y_coords in grouped_max_y_coordinates_dict.items():
        min_y = min(y_coords) - 10
        max_y = max(y_coords) + 10
        lines[line_name] = {'min_y': min_y, 'max_y': max_y, 'positions': []}

    lines['Unassigned'] = {'min_y': None, 'max_y': None, 'positions': []}

    def assign_positions_to_lines(marked_positions, lines):
        for item in marked_positions:
            label = item[0]
            position = item[1]

            # print(f"Processing label: {label}, position: {position}")

            if isinstance(position, tuple) and isinstance(position[0], int):
                positions = [position]
            elif isinstance(position, (list, tuple)) and all(isinstance(pos, tuple) and len(pos) == 2 for pos in position):
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
                        lines[line_name]['positions'].append({'label': label, 'x': x, 'y': y})
                        print(f"Assigned to {line_name}: label={label}, x={x}, y={y}")
                        assigned = True
                        break
                if not assigned:
                    lines['Unassigned']['positions'].append({'label': label, 'x': x, 'y': y})
                    print(f"Assigned to Unassigned: label={label}, x={x}, y={y}")


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

    total_labels = sum(len(line_info['positions']) for line_name, line_info in lines_info.items() if line_name != 'Unassigned')
    # print(f"\nTotal Labels: {total_labels}")

    return lines_info, total_labels , grouped_max_y_coordinates_array 

# ตัวอย่างการเรียกใช้งานฟังก์ชัน
# if __name__ == "__main__":
#     image_path = r"D:\BACKUP 06-08-2024\Desktop\project-1\image.png"
#     lines_info, total_labels ,max_x_coordinates= note_image(image_path)
#     print(f"\nTotal Labels: {total_labels} and {lines_info} and {max_x_coordinates}")

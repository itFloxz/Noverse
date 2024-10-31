import cv2
import numpy as np
from PIL import Image


def is_white_line(image, width, y):
    black_pixel_count = np.sum(image[y] == 0)
    return 0 if (black_pixel_count * 100 / width) > 28 else 1

def separate_y_coordinates(y_coordinates):
    sorted_coordinates = sorted(y_coordinates)
    merged_ranges = []
    current_range = [sorted_coordinates[0], sorted_coordinates[0]]
    for coord in sorted_coordinates[1:]:
        if coord - current_range[1] <= 2:
            current_range[1] = coord
        else:
            merged_ranges.append(tuple(current_range))
            current_range = [coord, coord]
    merged_ranges.append(tuple(current_range))
    max_coordinates = [max(range) for range in merged_ranges]
    return max_coordinates

def separate_x_coordinates(x_coordinates):
    sorted_coordinates = sorted(x_coordinates)
    merged_ranges = []
    current_range = [sorted_coordinates[0], sorted_coordinates[0]]
    for coord in sorted_coordinates[1:]:
        if coord - current_range[1] <= 2:
            current_range[1] = coord
        else:
            merged_ranges.append(tuple(current_range))
            current_range = [coord, coord]
    merged_ranges.append(tuple(current_range))
    max_coordinates = [max(range) for range in merged_ranges]
    return max_coordinates

def read_line(image_path):
    # image_load = cv2.imread(image_path)
    image_load = image_path
    image_load_array = np.array(image_load)
    gray_image = cv2.cvtColor(image_load_array, cv2.COLOR_RGB2GRAY)
    _, thresholded_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY)
    height, width = thresholded_image.shape
    black_rows = []
    start_x_coordinates = []
    for y in range(height):
        if is_white_line(thresholded_image, width, y):
            image_load_array[y, :, :] = 255
        else:
            black_rows.append(y)
            for x in range(width):
                if thresholded_image[y, x] == 0:
                    start_x_coordinates.append((y, x))
                    break
    min_y = min(black_rows)
    max_y = max(black_rows)
    y_range = max_y - min_y
    group_size = y_range // 5
    group_boundaries = [min_y + i * group_size for i in range(5)]
    group_boundaries.append(max_y)
    image_with_colored_points = image_load_array.copy()
    for i in range(5):
        start_y = group_boundaries[i]
        end_y = group_boundaries[i + 1]
        group_points = [y for y in black_rows if start_y <= y < end_y]
        for y in group_points:
            image_with_colored_points[y, :] = 0
    image_load_array[np.where((image_with_colored_points == [255, 255, 255]).all(axis=2))] = [255, 255, 255]
    image_load_modified = Image.fromarray(image_load_array)
    black_rows_all = len(black_rows)
    max_y_coordinates = separate_y_coordinates(black_rows)
    members_per_group = 5
    total_groups = len(max_y_coordinates) // members_per_group
    grouped_max_y_coordinates = [max_y_coordinates[i * members_per_group: (i + 1) * members_per_group] for i in range(total_groups)]
    subtraction_value = 12
    addition_value = 12
    for i, group in enumerate(grouped_max_y_coordinates):
        new_first_element = group[0] - subtraction_value
        grouped_max_y_coordinates[i] = [new_first_element] + group
        new_last_element = group[-1] + addition_value
        grouped_max_y_coordinates[i].append(new_last_element)
    y_coordinates_array = np.array(max_y_coordinates)
    grouped_max_y_coordinates_array = np.array(grouped_max_y_coordinates)
    start_y_coords, start_x_coords = zip(*start_x_coordinates)
    start_y_coords = np.array(start_y_coords)
    start_x_coords = np.array(start_x_coords)
    max_x_coordinates = separate_x_coordinates(start_x_coords)
    image_load_modified_array = np.array(image_load_modified)
    indices = np.where((image_load_array != image_load_modified_array).any(axis=2))
    image_load_modified_array[indices] = [255, 255, 255]
    modified_image = Image.fromarray(image_load_modified_array)
    return modified_image, grouped_max_y_coordinates_array, max_x_coordinates, start_y_coords


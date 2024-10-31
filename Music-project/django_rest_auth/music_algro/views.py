import os
import re
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from PIL import Image,ImageEnhance
import easyocr
from django.conf import settings
from django.http import JsonResponse
from django.utils.text import get_valid_filename
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from music21 import stream, note, environment, meter ,metadata
from django.core.files.storage import default_storage
import fitz
from .models import MusicFile,MusicSheet
from .serializers import MusicFileSerializer
from rest_framework.response import Response
import zipfile
from .utils.main import process_music_sheet
from .serializers import MusicSheetSerializer
from rest_framework import status

# Set MuseScore path globally
environment.set('musescoreDirectPNGPath', r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe')

def enhance_image_advanced(image_path, sharpness_factor=1.5, contrast_factor=1.0):
    """Enhances the image by adjusting sharpness, converting to grayscale, and increasing contrast."""
    try:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # เปิดภาพและแปลงเป็น Grayscale
        img = Image.open(image_path).convert("L")

        # ปรับความคมชัด (Sharpness)
        sharpener = ImageEnhance.Sharpness(img)
        sharpened_img = sharpener.enhance(sharpness_factor)

        # เพิ่ม Contrast
        contrast = ImageEnhance.Contrast(sharpened_img)
        enhanced_img = contrast.enhance(contrast_factor)

        # บันทึกภาพที่ปรับปรุงแล้ว
        enhanced_image_path = f"{os.path.splitext(image_path)[0]}_enhanced_advanced.png"
        enhanced_img.save(enhanced_image_path)

        print(f"Enhanced image saved at: {enhanced_image_path}")
        return enhanced_image_path

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Failed to enhance image: {e}")

    return None


def correct_text(detected_text):
    """Applies specific corrections to the OCR output."""
    correction_map = {
        "ุ": "ฺ", "ช": "ซ", "พ": "ฟ", "": "-","ู":"ฺ"
    }
    return ''.join(correction_map.get(char, char) for char in detected_text)

def map_to_universal_format(char):
    """Maps Thai characters to musical notes."""
    mappings = {
        'ด': 'C4', 'ร': 'D4', 'ม': 'E4', 'ฟ': 'F4',
        'ซ': 'G4', 'ล': 'A4', 'ท': 'B4', 'ดํ': 'C5',
        'รํ': 'D5', 'มํ': 'E5', 'ฟํ': 'F5', 'ซํ': 'G5',
        'ลํ': 'A5', 'ทํ': 'B5', 'ดฺ': 'C4', 'รฺ': 'D4',
        'มฺ': 'E4', 'ฟฺ': 'F4', 'ซฺ': 'G4', 'ลฺ': 'A4',
        'ทฺ': 'B4'
    }
    return mappings.get(char, char)

def transform_to_universal_format(text):
    """Transforms the corrected text to a universal music notation format."""
    universal_text = []
    i = 0
    while i < len(text):
        if i < len(text) - 1 and text[i + 1] in "ํฺ":
            universal_text.append(map_to_universal_format(text[i:i + 2]))
            i += 2
        else:
            universal_text.append(map_to_universal_format(text[i]))
            i += 1
    return ''.join(universal_text)

def extract_music_elements(text, pattern):
    """Extracts musical elements matching a given pattern."""
    return pattern.findall(text)

def create_music_score(elements, mapping,Musicname, time_signature='2/4', duration=0.5):
    """Creates a music score from elements using music21."""
    score = stream.Stream()
    score.metadata = metadata.Metadata()
    score.metadata.title = Musicname
    score.append(meter.TimeSignature(time_signature))
    for elem in elements:
        n = note.Rest(quarterLength=duration) if elem == '-' else note.Note(
            mapping.get(elem, elem), quarterLength=duration
        )
        score.append(n)
    return score


def pdf_to_images(pdf_path, output_folder):
    """Convert each PDF page to PNG and return a list of image paths."""
    pdf = fitz.open(pdf_path)  # เปิด PDF
    image_files = []
    os.makedirs(output_folder, exist_ok=True)  # สร้างโฟลเดอร์สำหรับเก็บภาพ

    # แปลงหน้าแรกแยกต่างหาก
    first_page = pdf.load_page(0)  # โหลดหน้าแรก
    first_pix = first_page.get_pixmap(dpi=600)  # แปลงเป็นภาพด้วย DPI 600
    first_page_path = os.path.join(output_folder, "preview_page_1.png")
    first_pix.save(first_page_path)  # บันทึกหน้าแรกเป็น PNG
    image_files.append(first_page_path)  # เพิ่มลงในลิสต์ไฟล์ภาพ

    # แปลงหน้าที่เหลือ (ถ้ามี) เป็น PNG
    for page_num in range(1, len(pdf)):
        page = pdf.load_page(page_num)  # โหลดหน้าถัดไป
        pix = page.get_pixmap(dpi=600)  # แปลงเป็นภาพ
        image_file = os.path.join(output_folder, f"page_{page_num}.png")
        pix.save(image_file)  # บันทึกภาพ
        image_files.append(image_file)  # เพิ่มไฟล์ลงลิสต์

    pdf.close()  # ปิด PDF
    return image_files  # คืนค่ารายการไฟล์ PNG

def create_zip_from_images(image_files, zip_filename):
    """Create a zip file from a list of images."""
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for image_file in image_files:
            zipf.write(image_file, os.path.basename(image_file))  # เขียนไฟล์ลงใน ZIP
    return zip_filename  # คืนชื่อไฟล์ ZIP



@api_view(['POST'])
@permission_classes([AllowAny])
def process_music_ocr(request):
    """Processes uploaded music files through OCR, generates PNGs, and creates a zip."""
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    # รับไฟล์ที่อัปโหลดและตั้งชื่อไฟล์พื้นฐาน
    file = request.FILES['file']
    original_name = get_valid_filename(file.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    username = request.user.email if request.user.is_authenticated else 'guest'

    # กำหนดเส้นทางไฟล์ต่าง ๆ
    base_name = f"{username}_{timestamp}"
    media_root = settings.MEDIA_ROOT
    output_folder = os.path.join(media_root, base_name)

    # สร้างโฟลเดอร์หลักสำหรับเก็บผลลัพธ์
    os.makedirs(output_folder, exist_ok=True)

    # กำหนดเส้นทางของไฟล์ต่าง ๆ ภายในโฟลเดอร์ที่สร้าง
    file_path = os.path.join(output_folder, f"original_{original_name}.png")
    pdf_output = os.path.join(output_folder, "output_music_score.pdf")
    png_output = os.path.join(output_folder, "output_music_score")
    zip_output = os.path.join(output_folder, "images.zip")

    # สร้างโฟลเดอร์ถ้ายังไม่มี
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)  # บันทึกไฟล์ที่อัปโหลด
    except IOError as e:
        return JsonResponse({"error": f"Failed to save file: {e}"}, status=500)

    # Enhance the image for better OCR
    enhanced_image = enhance_image_advanced(file_path, sharpness_factor=2, contrast_factor=1.0)
    if not enhanced_image:
        return JsonResponse({"error": "Failed to enhance image"}, status=500)

    # OCR processing
    reader = easyocr.Reader(['th'])
    ocr_results = reader.readtext(enhanced_image, detail=0, allowlist="ดรมฟซลท-ฺํุูช",min_size=11)
    corrected = [correct_text(line) for line in ocr_results]
    universal_results = {f"box_{i}": transform_to_universal_format(line) for i, line in enumerate(corrected)}
    print(ocr_results)
    print(corrected)
    print(universal_results)
    # สร้างโน้ตดนตรีจากผลลัพธ์ OCR
    pattern = re.compile(r'C#?4|D#?4|E#?4|F#?4|G#?4|A#?4|B#?4|C#?5|D#?5|E#?5|F#?5|G#?5|A#?5|B#?5|-')
    elements = [elem for text in universal_results.values() for elem in extract_music_elements(text, pattern)]

    natural_mapping = {f"{n}#4": f"{n}4" for n in "CDEFGAB"} | {f"{n}#5": f"{n}5" for n in "CDEFGAB"}
    score = create_music_score(elements, natural_mapping , original_name)

    try:
        score.write('musicxml.pdf', pdf_output)
    except Exception as e:
        return JsonResponse({"error": f"Failed to create PDF: {e}"}, status=500)

    # Convert PDF to PNG and create a zip file
    try:
        image_files = pdf_to_images(pdf_output, png_output)  # แปลง PDF เป็น PNG
        zip_file = create_zip_from_images(image_files, zip_output)  # สร้าง ZIP จาก PNG
    except Exception as e:
        return JsonResponse({"error": f"Failed to generate zip: {e}"}, status=500)

    # สร้าง URL สำหรับดาวน์โหลด PDF และ ZIP
    png_url = request.build_absolute_uri(settings.MEDIA_URL + f"{base_name}/output_music_score/preview_page_1.png")
    pdf_url = request.build_absolute_uri(settings.MEDIA_URL + f"{base_name}/output_music_score.pdf")
    zip_url = request.build_absolute_uri(settings.MEDIA_URL + f"{base_name}/images.zip")

    # บันทึกลงฐานข้อมูลถ้าผู้ใช้ล็อกอิน
    if request.user.is_authenticated:
        MusicFile.objects.create(
            user=request.user,
            original_file_name=original_name,
            pdf_file_path=pdf_url,
            png_file_path=zip_url
        )

    # ส่ง URL กลับไปยังผู้ใช้
    return JsonResponse({
        "message": "Processing complete",
        "pdf_url": pdf_url,
        "zip_url": zip_url,
        "png_url": png_url,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_music_history(request):
    user = request.user  # ดึง user ที่ทำการ authenticated
    music_files = MusicFile.objects.filter(user=user).order_by('-created_at')  # เรียงตามวันที่ล่าสุด
    serializer = MusicFileSerializer(music_files, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def music_sheet_upload(request):
    # รับค่าจาก request.data โดยตรง
    image = request.FILES.get('image')
    title_text = request.data.get('title_text')
    key = request.data.get('key',)
    tempo = request.data.get('tempo')
    clef_type = request.data.get('clef_type')
    clef_music = request.data.get('clef_music')

    if not image:
        return JsonResponse({"error": "Image file is required."}, status=400)

    # สร้างเส้นทางสำหรับบันทึกไฟล์
    original_name = get_valid_filename(image.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    username = request.user.email if request.user.is_authenticated else 'guest'
    base_name = f"{username}_{timestamp}"
    media_root = settings.MEDIA_ROOT
    output_folder = os.path.join(media_root, base_name)
    os.makedirs(output_folder, exist_ok=True)

    # กำหนดเส้นทางสำหรับบันทึกไฟล์
    image_path = os.path.join(output_folder, f"original_{original_name}")
    pdf_output = os.path.join(output_folder, "output_music_score.pdf")
    image_result = os.path.join(output_folder, "output_music_score")

    # บันทึกไฟล์ภาพที่อัปโหลด
    try:
        with open(image_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)
    except IOError as e:
        return JsonResponse({"error": f"Failed to save file: {e}"}, status=500)

    # ประมวลผลและสร้าง PDF
    process_music_sheet(
        image_path=image_path,
        output_pdf_path=pdf_output,
        title_text=title_text,
        key=key,
        tempo=tempo,
        clef_type=clef_type,
        clef_music=clef_music
    )
    image_file = pdf_to_images(pdf_output, image_result)
    png_url = request.build_absolute_uri(settings.MEDIA_URL + f"{base_name}/output_music_score/preview_page_1.png")
    pdf_url = request.build_absolute_uri(settings.MEDIA_URL + f"{base_name}/output_music_score.pdf")

    # เข้ารหัส PDF เป็น base64
    try:
        with open(pdf_output, "rb") as pdf_file:
            pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
    except IOError as e:
        return JsonResponse({"error": f"Failed to read generated PDF file: {e}"}, status=500)

    # บันทึกข้อมูลลงฐานข้อมูลถ้าผู้ใช้เข้าสู่ระบบแล้ว
    if request.user.is_authenticated:
        MusicSheet.objects.create(
            user=request.user,
            image_path=png_url,
            pdf_path=pdf_url,
            title_text=title_text,
            key=key,
            tempo=tempo,
            clef_type=clef_type,
            clef_music=clef_music
        )

    return JsonResponse({
        "message": "File processed successfully",
        "pdf_base64": pdf_base64,
        "pdf_url": pdf_url,
        "image_url": png_url
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_view(request):
    user = request.user
    music_sheets = MusicSheet.objects.filter(user=user).order_by('-created_at')
    serializer = MusicSheetSerializer(music_sheets, many=True)
    return Response(serializer.data)

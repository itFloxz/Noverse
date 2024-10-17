import os
import re
from datetime import datetime
from PIL import Image, ImageFilter
import easyocr
from django.conf import settings
from django.http import JsonResponse
from django.utils.text import get_valid_filename
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from music21 import stream, note, environment, meter
import fitz
from .models import MusicFile

# Set MuseScore path globally
environment.set('musescoreDirectPNGPath', r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe')

def enhance_image(image_path):
    """Enhances the image by applying a sharpening filter."""
    try:
        img = Image.open(image_path)
        sharpened_image = img.filter(ImageFilter.SHARPEN)
        sharpened_image_path = f"{os.path.splitext(image_path)[0]}_sharpened.png"
        sharpened_image.save(sharpened_image_path)
        return sharpened_image_path
    except Exception as e:
        print(f"Failed to enhance image: {e}")
        return None

def correct_text(detected_text):
    """Applies specific corrections to the OCR output."""
    correction_map = {
        "ุู": "ฺ", "ช": "ซ", "พ": "ฟ", "": "-"
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

def create_music_score(elements, mapping, time_signature='2/4', duration=0.5):
    """Creates a music score from elements using music21."""
    score = stream.Stream()
    score.append(meter.TimeSignature(time_signature))
    for elem in elements:
        n = note.Rest(quarterLength=duration) if elem == '-' else note.Note(
            mapping.get(elem, elem), quarterLength=duration
        )
        score.append(n)
    return score

def pdf_to_png(pdf_path, output_path):
    """Converts a PDF file to PNG images."""
    pdf = fitz.open(pdf_path)
    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        pix = page.get_pixmap(dpi=600)
        pix.save(f"{output_path}_{page_num}.png")
    pdf.close()

@api_view(['POST'])
@permission_classes([])  # Remove IsAuthenticated to allow public access
def process_music_ocr(request):
    """Processes uploaded music files through OCR and generates outputs."""
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES['file']
    original_name = get_valid_filename(file.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # If user is logged in, get their email; otherwise, use 'guest'
    username = request.user.email if request.user.is_authenticated else 'guest'

    # Create unique file names and paths
    base_name = f"{username}_{timestamp}"
    media_root = settings.MEDIA_ROOT
    file_path = os.path.join(media_root, f"{base_name}_original_{original_name}")
    pdf_output = os.path.join(media_root, f"{base_name}_output_music_score.pdf")
    png_output = os.path.join(media_root, f"{base_name}_output_music_score")

    # Save the uploaded file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
    except IOError as e:
        return JsonResponse({"error": f"Failed to save file: {e}"}, status=500)

    sharpened_image = enhance_image(file_path)
    if not sharpened_image:
        return JsonResponse({"error": "Failed to enhance image"}, status=500)

    # OCR processing
    reader = easyocr.Reader(['th'])
    ocr_results = reader.readtext(sharpened_image, detail=0, allowlist="ดรมฟซลท-ฺํุู")
    corrected = [correct_text(line) for line in ocr_results]
    universal_results = {f"box_{i}": transform_to_universal_format(line) for i, line in enumerate(corrected)}

    # Extract musical elements
    pattern = re.compile(r'C#?4|D#?4|E#?4|F#?4|G#?4|A#?4|B#?4|C#?5|D#?5|E#?5|F#?5|G#?5|A#?5|B#?5|-')
    elements = [elem for text in universal_results.values() for elem in extract_music_elements(text, pattern)]

    # Create and save the music score
    natural_mapping = {f"{n}#4": f"{n}4" for n in "CDEFGAB"} | {f"{n}#5": f"{n}5" for n in "CDEFGAB"}
    score = create_music_score(elements, natural_mapping)

    try:
        score.write('musicxml.pdf', pdf_output)
    except Exception as e:
        return JsonResponse({"error": f"Failed to create PDF: {e}"}, status=500)

    try:
        pdf_to_png(pdf_output, png_output)
    except Exception as e:
        return JsonResponse({"error": f"Failed to convert PDF to PNG: {e}"}, status=500)

    # Save to database only if the user is authenticated
    if request.user.is_authenticated:
        MusicFile.objects.create(
            user=request.user,
            original_file_name=original_name,
            pdf_file_path=pdf_output,
            png_file_path=f"{png_output}_0.png"
        )

    pdf_url = request.build_absolute_uri(settings.MEDIA_URL + f"{base_name}_output_music_score.pdf")
    png_url = request.build_absolute_uri(settings.MEDIA_URL + f"{base_name}_output_music_score_0.png")

    return JsonResponse({
        "message": "Processing complete",
        "pdf_url": pdf_url,
        "png_url": png_url,
    })


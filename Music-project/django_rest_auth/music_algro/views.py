import os
import re
from PIL import Image, ImageFilter
import easyocr
from django.conf import settings
from django.http import JsonResponse
from music21 import stream, note, environment, meter
import fitz
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from django.utils.text import get_valid_filename

# Set the path to the MuseScore executable
environment.set('musescoreDirectPNGPath', r'C:\Program Files\MuseScore 4\bin\MuseScore4.exe')

def enhance_image(image_path):
    """
    Enhance the clarity of the image by applying sharpening filters.
    """
    try:
        with Image.open(image_path) as img:
            # Apply a sharpening filter
            sharpened_image = img.filter(ImageFilter.SHARPEN)
            
            # Save the sharpened image
            sharpened_image_path = os.path.splitext(image_path)[0] + '_sharpened.png'
            sharpened_image.save(sharpened_image_path)
            
            return sharpened_image_path
    except Exception as e:
        print(f"Failed to enhance image: {e}")
        return None

def correct_text(detected_text):
    correction_map = {
        "ุู": "ฺ",
        "ช": "ซ",
        "พ": "ฟ",
        "": "-"
    }
    return ''.join([correction_map.get(char, char) for char in detected_text])

def map_to_universal_format(char):
    mappings = {
        'ด': 'C4', 'ร': 'D4', 'ม': 'E4', 'ฟ': 'F4',
        'ซ': 'G4', 'ล': 'A4', 'ท': 'B4', 'ดํ': 'C5',
        'รํ': 'D5', 'มํ': 'E5', 'ฟํ': 'F5',
        'ซํ': 'G5', 'ลํ': 'A5', 'ทํ': 'B5',
        'ดฺ': 'C4', 'รฺ': 'D4', 'มฺ': 'E4', 'ฟฺ': 'F4',
        'ซฺ': 'G4', 'ลฺ': 'A4', 'ทฺ': 'B4'
    }
    return mappings.get(char, char)

def transform_to_universal_format(corrected_text):
    universal_text = ""
    i = 0
    while i < len(corrected_text):
        if i < len(corrected_text) - 1 and corrected_text[i + 1] in "ํฺ":
            universal_text += map_to_universal_format(corrected_text[i:i + 2])
            i += 2
        else:
            universal_text += map_to_universal_format(corrected_text[i])
            i += 1
    return universal_text

def extract_music_elements(text, pattern):
    return pattern.findall(text)

def create_music_score(elements, mapping, time_signature='2/4', duration=0.5):
    score = stream.Stream()
    score.append(meter.TimeSignature(time_signature))
    for elem in elements:
        if elem == '-':
            n = note.Rest(quarterLength=duration)
        else:
            n = note.Note(mapping.get(elem, elem), quarterLength=duration)
        score.append(n)
    return score

def pdf_to_png(pdf_path, output_png_path):
    # Open the provided PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Loop through each page in the PDF
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        
        
        pix = page.get_pixmap(dpi=600)
        
        pix.save(f"{output_png_path}_{page_number}.png")
    
    pdf_document.close()

@api_view(['POST'])
def process_music_ocr(request):
    parser_classes = (MultiPartParser,)
    
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    file = request.FILES['file']
    file_name = get_valid_filename(file.name)
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Save the uploaded file
    try:
        with open(file_path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
    except IOError as e:
        return JsonResponse({"error": f"Failed to save file: {str(e)}"}, status=500)

    # Enhance the image quality
    sharpened_image_path = enhance_image(file_path)
    if not sharpened_image_path:
        return JsonResponse({"error": "Failed to enhance image"}, status=500)

    # Perform OCR using EasyOCR on the sharpened image
    reader = easyocr.Reader(['th'])
    ocr_results = reader.readtext(sharpened_image_path, detail=0,allowlist="ดรมฟซลท-ฺํุู")

    # Further processing (same as your original code)
    corrected_results = [correct_text(line) for line in ocr_results]
    universal_results = {f"box_{i}": transform_to_universal_format(line) for i, line in enumerate(corrected_results)}

    # Extract musical notes and rests from the universal format
    note_pattern = re.compile(r'C#?4|D#?4|E#?4|F#?4|G#?4|A#?4|B#?4|C#?5|D#?5|E#?5|F#?5|G#?5|A#?5|B#?5|-')
    extracted_elements = [elem for text in universal_results.values() for elem in extract_music_elements(text, note_pattern)]

    # Create and save the music score
    natural_note_mapping = {
        'C#4': 'C4', 'D#4': 'D4', 'E#4': 'E4', 'F#4': 'F4',
        'G#4': 'G4', 'A#4': 'A4', 'B#4': 'B4', 'C#5': 'C5',
        'D#5': 'D5', 'E#5': 'E5', 'F#5': 'F5', 'G#5': 'G5',
        'A#5': 'A5', 'B#5': 'B5'
    }
    score = create_music_score(extracted_elements, natural_note_mapping)
    pdf_output = os.path.join(settings.MEDIA_ROOT, 'output_music_score.pdf')
    try:
        score.write('musicxml.pdf', pdf_output)
    except Exception as e:
        return JsonResponse({"error": f"Failed to create PDF: {str(e)}"}, status=500)

    # Convert the PDF to PNG
    try:
        pdf_to_png(pdf_output, os.path.join(settings.MEDIA_ROOT, 'output_music_score'))
    except Exception as e:
        return JsonResponse({"error": f"Failed to convert PDF to PNG: {str(e)}"}, status=500)

    pdf_url = request.build_absolute_uri(settings.MEDIA_URL + 'output_music_score.pdf')
    png_url = request.build_absolute_uri(settings.MEDIA_URL + 'output_music_score_0.png')
    
    return JsonResponse({
        "message": "Processing complete",
        "pdf_url": pdf_url,
        "png_url": png_url
    })

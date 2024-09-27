from django.urls import path
from .views import process_music_ocr

urlpatterns = [
    path('process-music-ocr/', process_music_ocr, name='process_music_ocr'),
]

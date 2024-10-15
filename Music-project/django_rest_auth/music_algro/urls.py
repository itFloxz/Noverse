from django.urls import path

from . import views
urlpatterns = [
    path('process-music-ocr/', views.process_music_ocr, name='process_music_ocr'),
]

from django.urls import path
from . import views
urlpatterns = [
    path('process-music-ocr/', views.process_music_ocr, name='process_music_ocr'),
    path('music-history/', views.user_music_history, name='user-music-history'),
    path('process_custom_music_sheet/',views.music_sheet_upload,name='music_sheet_upload'),
    
]

from django.urls import path
from .views import MusicSheetUploadView
from . import views
urlpatterns = [
    path('process-music-ocr/', views.process_music_ocr, name='process_music_ocr'),
    path('music-history/', views.user_music_history, name='user-music-history'),
    path('process_custom_music_sheet/',MusicSheetUploadView.as_view(),name='process_custom_music_sheet')
]

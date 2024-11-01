from rest_framework import serializers
from .models import MusicFile,MusicSheet

class MusicFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicFile
        fields = ['id', 'original_file_name', 'pdf_file_path', 'png_file_path', 'created_at']



class MusicSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicSheet
        fields = ['id', 'image_path', 'pdf_path', 'title_text', 'key', 'tempo', 'clef_type', 'clef_music', 'created_at']

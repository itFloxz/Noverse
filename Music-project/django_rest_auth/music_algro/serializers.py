from rest_framework import serializers
from .models import MusicFile

class MusicFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicFile
        fields = ['id', 'original_file_name', 'pdf_file_path', 'png_file_path', 'created_at']

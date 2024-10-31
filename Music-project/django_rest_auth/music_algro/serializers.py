from rest_framework import serializers
from .models import MusicFile

class MusicFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicFile
        fields = ['id', 'original_file_name', 'pdf_file_path', 'png_file_path', 'created_at']


class MusicSheetSerializer(serializers.Serializer):
    image = serializers.ImageField()
    title_text = serializers.CharField(max_length=100, default="เพลง บรรเลงใจ")
    key = serializers.CharField(max_length=50, default="C Major")
    tempo = serializers.CharField(max_length=50, default="120 BPM")
    clef_type = serializers.CharField(max_length=20, default="classic")
    clef_music = serializers.CharField(max_length=1, default="G")
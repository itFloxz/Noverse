from django.db import models
from accounts.models import User

# Create your models here.from django.db import models

class MusicFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # เชื่อมโยงกับ User model
    original_file_name = models.CharField(max_length=255)
    pdf_file_path = models.CharField(max_length=255)
    png_file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_file_name
    
class MusicSheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_path = models.CharField(max_length=255)  # Changed to store file path as string
    pdf_path = models.CharField(max_length=255)
    title_text = models.CharField(max_length=100)
    key = models.CharField(max_length=50)
    tempo = models.CharField(max_length=50)
    clef_type = models.CharField(max_length=20)
    clef_music = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title_text} by {self.user.get_full_name}"
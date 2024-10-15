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
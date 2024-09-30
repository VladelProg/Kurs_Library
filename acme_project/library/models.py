from django.db import models

class LibraryFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')  # Загруженные файлы будут храниться в media/files/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

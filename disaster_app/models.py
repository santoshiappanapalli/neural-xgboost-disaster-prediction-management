from django.db import models

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='dataset/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

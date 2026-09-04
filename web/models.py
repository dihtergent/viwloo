from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class images(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='posts')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title or f"Image #{self.id}"
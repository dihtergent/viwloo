from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class images(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    image = CloudinaryField('image')

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = CloudinaryField('avatar', blank=True, null=True)
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.display_name or self.user.username

    @property
    def post_count(self):
        return self.user.posts.count()


CATEGORY_CHOICES = [
    ('recommended', 'Recommended'),
    ('itinerary', 'Itinerary'),
    ('route', 'Route'),
    ('proxy', 'Proxy Level'),
]


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='recommended')
    views_count = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def google_maps_url(self):
        if self.has_location:
            return f'https://www.google.com/maps?q={self.latitude},{self.longitude}'
        return ''


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} on {self.post.title}'


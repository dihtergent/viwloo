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
    ('interknot', 'Interknot'),
    ('proxy', 'Proxy'),
]


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='interknot')
    views_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(id=user.id).exists()

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def google_maps_url(self):
        if self.has_location:
            return f'https://www.google.com/maps?q={self.latitude},{self.longitude}'
        return ''

    @property
    def expires_at(self):
        from datetime import timedelta
        return self.created_at + timedelta(days=100)

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() >= self.expires_at

    @property
    def time_left_display(self):
        from django.utils import timezone
        now = timezone.now()
        if now >= self.expires_at:
            return "Expired"
        
        diff = self.expires_at - now
        days = diff.days
        total_seconds = int(diff.total_seconds())

        if days > 2:
            return f"{days} days left"
        else:
            hours = total_seconds // 3600
            if hours >= 1:
                return f"{hours} hours left"
            else:
                minutes = max(1, total_seconds // 60)
                return f"{minutes} min left"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} on {self.post.title}'


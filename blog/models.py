from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from functools import partial

from blog.validators import file_size_validator


class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='author')
    bio = models.TextField(blank=True, null=True)
    follower_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='users/profiles/', null=True, blank=True,
                              default='users/profiles/default.png',
                              validators=[file_size_validator]
                              )
    following_count = models.PositiveIntegerField(default=0)
    follows = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='followed_by'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    
class Post(models.Model):
    STATUS_CHOICES = [
        ('D', "Draft"),
        ('P', "Published")
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    body = models.TextField()
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    published_date = models.DateTimeField(null=True, blank=True, )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == 'P' and not self.published_date:
            self.published_date = timezone.now()
        elif self.status == 'D':
            self.published_date = None
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date', '-created_at']
        
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog/post_images/', validators=[file_size_validator])
    caption = models.CharField(max_length=255, blank=True, null=True)
    upload_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.post.title}"

class PostVideo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='blog/post_videos/', validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'avi', 'mov']), partial(file_size_validator, max_size_in_mb=10)])
    caption = models.CharField(max_length=255, blank=True, null=True)
    upload_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for {self.post.title}"


class Comment(models.Model):
    owner = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    def __str__(self):
        return f"Comment by {self.owner.user.username} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}"

    def is_reply(self):
        return self.parent is not None


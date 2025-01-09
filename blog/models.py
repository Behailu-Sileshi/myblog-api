from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='users/profiles/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    follows = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='followed_by'
    )

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


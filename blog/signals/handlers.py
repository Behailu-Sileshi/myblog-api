from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.db.models.signals import m2m_changed

from blog.models import Author

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_an_author_for_new_user(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(user=instance)
        



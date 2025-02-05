# Generated by Django 5.1.5 on 2025-01-16 09:06

import blog.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import functools
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_author_follower_count_author_following_count"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="joined_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="author",
            name="image",
            field=models.ImageField(
                blank=True,
                default="users/profiles/default.png",
                null=True,
                upload_to="users/profiles/",
                validators=[blog.validators.file_size_validator],
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="author",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="PostImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        upload_to="blog/post_images/",
                        validators=[blog.validators.file_size_validator],
                    ),
                ),
                ("caption", models.CharField(blank=True, max_length=255, null=True)),
                ("upload_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="blog.post",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PostVideo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "video",
                    models.FileField(
                        upload_to="blog/post_videos/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["mp4", "mkv", "avi", "mov"]
                            ),
                            functools.partial(
                                blog.validators.file_size_validator,
                                *(),
                                **{"max_size_in_mb": 10}
                            ),
                        ],
                    ),
                ),
                ("caption", models.CharField(blank=True, max_length=255, null=True)),
                ("upload_at", models.DateTimeField(auto_now_add=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="blog.post",
                    ),
                ),
            ],
        ),
    ]

from django.db import models
from django.contrib.auth.models import User
import uuid

AUTHOR_CHOICES = [
    ('user', 'User'),
    ('system', 'System'),
]

class Knowledge(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='knowledge', 
        verbose_name='User'
    )
    title = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Knowledge'
        verbose_name_plural = 'Knowledge'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Message(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='messages', 
        verbose_name='User'
    )
    content = models.TextField()
    author = models.CharField(max_length=10, choices=AUTHOR_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']

    def __str__(self):
        return self.content
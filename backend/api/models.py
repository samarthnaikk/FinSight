from django.db import models
from django.conf import settings
from django.utils import timezone

class ConfidentialData(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="confidential_data"
    )
    encrypted_payload = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"ConfidentialData(user={self.user_id}, id={self.id})"

class NonConfidentialData(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="non_confidential_data"
    )
    encrypted_payload = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"NonConfidentialData(user={self.user_id}, id={self.id})"

class ChatMemory(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_memory"
    )
    encrypted_messages = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ChatMemory(user={self.user_id})"

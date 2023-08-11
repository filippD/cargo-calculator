from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    is_premium = models.BooleanField(default=False)
    searches_left = models.IntegerField(default=5)

class UserSession(models.Model):
    searches_left = models.IntegerField(default=5)
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']


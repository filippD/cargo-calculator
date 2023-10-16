from django.db import models
import uuid

class UserSession(models.Model):
  searches_left = models.IntegerField(default=3)
  session_id = models.UUIDField(default=uuid.uuid4, editable=False)
  created_on = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['created_on']
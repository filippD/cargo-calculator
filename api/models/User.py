from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class WorkTypes(models.TextChoices):
        BROKER = 'broker'
        AIRCRAFT_OPERATOR = 'aircraft_operator'

    work_type = models.CharField(
        max_length=255,
        choices=WorkTypes.choices,
        default=WorkTypes.BROKER,
    )
    is_premium = models.BooleanField(default=False)
    searches_left = models.IntegerField(default=3)
    max_searches = models.IntegerField(default=3)
    company_name = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
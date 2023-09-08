from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

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
    company_name = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)


class UserSession(models.Model):
    searches_left = models.IntegerField(default=3)
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

class CharterHistory(models.Model):
    number_of_flights = models.IntegerField(default=0)
    departure_city = models.CharField(max_length=255)
    arrival_city = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.departure_city} - {self.arrival_city}"

    class Meta:
        ordering = ['created_on']


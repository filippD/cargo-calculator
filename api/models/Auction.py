from django.db import models
from .User import User
import uuid

class Auction(models.Model):
  class CargoTypes(models.TextChoices):
    GENERAL = 'general'
    MILITARY = 'military'
    DANGEROUS = 'dangerous'
    LIVESTOCK = 'livestock'
    PERISHABLE = 'perishable'

  cargo_type = models.CharField(max_length=255, choices=CargoTypes.choices)
  departure_airport = models.CharField(max_length=255)
  arrival_airport = models.CharField(max_length=255)
  departure_date = models.DateTimeField()
  payload = models.IntegerField()
  expiration_date = models.DateTimeField()
  date_flexibility_days = models.IntegerField(default=0)
  location_flexibility_km = models.IntegerField(default=0)
  notes = models.TextField()
  created_on = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  strong_id = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)

  class Meta:
    ordering = ['created_on']

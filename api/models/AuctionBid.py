from django.db import models
from .Auction import Auction

class AuctionBid(models.Model):
  class AuctionBidTypes(models.TextChoices):
    GENERATED = 'generated'
    CONFIRMED = 'confirmed'

  bid_type = models.CharField(max_length=255, choices=AuctionBidTypes.choices)
  auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
  operator = models.CharField(max_length=255)
  aircraft = models.CharField(max_length=255)
  flight_duration = models.CharField(max_length=255)
  price = models.IntegerField()
  price_currency = models.CharField(max_length=3)
  operator_email = models.CharField(max_length=255)
  operator_phone = models.CharField(max_length=255)
  operator_note = models.TextField()
  created_on = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['created_on']

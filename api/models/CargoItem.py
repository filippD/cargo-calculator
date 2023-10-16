from django.db import models
from .Auction import Auction

class CargoItem(models.Model):
  x_dimension = models.IntegerField(default=0)
  y_dimension = models.IntegerField(default=0)
  z_dimension = models.IntegerField(default=0)

  auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
  created_on = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering = ['created_on']

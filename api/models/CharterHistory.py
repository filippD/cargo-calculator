from django.db import models

class CharterHistory(models.Model):
  number_of_flights = models.IntegerField(default=0)
  departure_city = models.CharField(max_length=255)
  arrival_city = models.CharField(max_length=255)
  created_on = models.DateTimeField(auto_now_add=True)


  def __str__(self):
    return f"{self.departure_city} - {self.arrival_city}"

  class Meta:
    ordering = ['created_on']


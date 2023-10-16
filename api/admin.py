from django.contrib import admin
from .models.User import User
from .models.CharterHistory import CharterHistory
from .models.Auction import Auction
from .models.AuctionBid import AuctionBid

# Register your models here.
admin.site.register([
  User,
  CharterHistory,
  Auction,
  AuctionBid
])

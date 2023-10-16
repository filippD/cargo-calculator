from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import json
import environ
from ..models import Auction
from django.forms.models import model_to_dict
from django.core.paginator import Paginator
import datetime
import pytz
from rest_framework.permissions import IsAuthenticated

class AuctionsExpireApiView(APIView):
  permission_classes = (IsAuthenticated, )

  def post(self, request, auction_id, *args, **kwargs):
    try:
      auction = Auction.objects.get(strong_id=auction_id)
      print(request.user.id)
      if request.user.id is not auction.user_id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

      utc=pytz.UTC
      Auction.objects.filter(strong_id=auction_id).update(expiration_date=utc.localize(datetime.datetime.today()))
      auction = Auction.objects.get(strong_id=auction_id)
      resp = {
        'id': auction.id,
        'cargo_type': auction.cargo_type,
        'departure_airport': auction.departure_airport,
        'arrival_airport': auction.arrival_airport,
        'departure_date': auction.departure_date.strftime("%d.%m.%Y"),
        'departure_time': auction.departure_date.strftime("%H:%M"),
        'expiration_time': auction.expiration_date.strftime("%H:%M"),
        'expiration_date': auction.expiration_date.strftime("%d.%m.%Y"),
        'payload': auction.payload,
        'date_flexibility_days': auction.date_flexibility_days,
        'location_flexibility_km': auction.location_flexibility_km,
        'notes': auction.notes,
        "active": auction.expiration_date > utc.localize(datetime.datetime.today()),
        'bids': map(
          lambda bid: {
            'id': bid.id,
            'type': bid.bid_type,
            'operator': bid.operator,
            'aircraft': bid.aircraft,
            'flight_duration': bid.flight_duration,
            'price': bid.price,
            'price_currency': bid.price_currency,
            'operator_email': bid.operator_email,
            'operator_phone': bid.operator_phone,
            'operator_note': bid.operator_note
          },
          list(auction.auctionbid_set.all())
        )
      }
      return Response(resp, status=status.HTTP_200_OK)
    except:
      return Response(status=status.HTTP_404_NOT_FOUND)

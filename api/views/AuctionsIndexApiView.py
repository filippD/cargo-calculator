from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ..models import Auction, AuctionBid
import datetime
import json
from rest_framework.permissions import IsAuthenticated
import pytz

class AuctionsIndexApiView(APIView):
  permission_classes = (IsAuthenticated, )

  def post(self, request):
    params = json.loads(request.body)
    search_active = params.get('active') is True
    search_historical = params.get('active') is False
    by_user = params.get('my')
    utc=pytz.UTC
    if search_active:
      start_date = datetime.datetime.today()
      end_date=datetime.datetime(9999, 12, 31)
    elif search_historical:
      start_date = datetime.datetime(1, 1, 1)
      end_date=datetime.datetime.today()
    else:
      start_date = datetime.datetime(1, 1, 1)
      end_date=datetime.datetime(9999, 12, 31)
    
    auctions = Auction.objects.filter(expiration_date__range=[utc.localize(start_date), utc.localize(end_date)])
    if by_user:
      auctions = auctions.filter(user_id=request.user.id)

    resp = map(
      lambda auction: {
        'id': auction.strong_id,
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
      },
      list(auctions.order_by('-id')[:5])
    )
    return Response(resp, status=status.HTTP_200_OK)

  permission_classes = []
  def get(self, request):
    bid = AuctionBid.objects.filter(bid_type="confirmed").last()
    if not bid:
      return Response(status=status.HTTP_404_NOT_FOUND)
    auction = Auction.objects.get(pk=bid.auction_id)

    resp = {
        'id': auction.strong_id,
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

  

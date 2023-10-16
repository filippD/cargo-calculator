from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import json
import re
from ..models import Auction, AuctionBid, CargoItem
from rest_framework.permissions import IsAuthenticated
from api.calculator.Client import Client
import requests
import environ

class AuctionsCreateApiView(APIView):
  permission_classes = (IsAuthenticated, )
  def post(self, request, *args, **kwargs):
    # try:
      params = json.loads(request.body)
      env = environ.Env()
      environ.Env.read_env()
      auction = Auction(
        cargo_type=params.get("cargo_type"),
        departure_airport=params.get("arr_origin"),
        arrival_airport=params.get("arr_destination"),
        departure_date=params.get('departure_date').split('T')[0] + "T" + params.get("departure_time"),
        expiration_date=params.get('expiration_date').split('T')[0] + "T" + params.get("expiration_time"),
        payload=params.get("payload"),
        date_flexibility_days=params.get("date_flexibility_days"),
        location_flexibility_km=params.get("location_flexibility_km"),
        notes=params.get("notes"),
        user_id=request.user.id
      )
      auction.save()
      auction = Auction.objects.get(pk=auction.id)
      for item_params in params.get("cargo_items", []):
        cargo_item = CargoItem(
          x_dimension=item_params.get("h"),
          y_dimension=item_params.get("w"),
          z_dimension=item_params.get("l"),
          auction_id=auction.id
        )
        cargo_item.save()
        response = Client.calculate({
          "arr_origin": params.get("arr_origin"),
          "arr_destination": params.get("arr_destination"),
          "date": params.get('departure_date'),
          "payload": params.get("payload"),
          "time_critical": True,
          "charter": True,
          "one_leg": True,
          "cargo_items": params.get("cargo_items", [])
        })
        for generated_bid in response[:5]:
          price, currency = generated_bid.get("Price").split(" ")
          bid = AuctionBid(
            bid_type="generated",
            auction_id=auction.id, 
            operator=generated_bid.get("Operator"),
            aircraft=generated_bid.get("Aircraft"),
            flight_duration=generated_bid.get("Flight Time"),
            price=int(re.sub(",", "", price)),
            price_currency=currency,
            operator_email=generated_bid.get("Email"),
            operator_phone=generated_bid.get("Phone")
          )
          bid.save()
      requests.post(
        f'https://api.telegram.org/bot{env("BOT_TOKEN")}/sendMessage',
        json={'chat_id': env('TG_CHAT_ID'), 'text': f'New auction request https://airmission.aero/auctions/{auction.strong_id}'}
      )
      return Response({
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
      }, status=status.HTTP_200_OK)
    # except:
    #   return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

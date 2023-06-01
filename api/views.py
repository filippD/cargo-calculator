from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.calculator.Client import Client
from api.Airports import Airports
import json
import time

class CalculateApiView(APIView):
    def post(self, request, *args, **kwargs):
        response = Client.calculate(json.loads(request.body))
        time.sleep(1)
        return Response(response, status=status.HTTP_200_OK)

class RequestsApiView(APIView):
    def post(self, request, *args, **kwargs):
        Client.send_request(json.loads(request.body))
        return Response(status=status.HTTP_200_OK)

class AirportsApiView(APIView):
    def post(self, request, *args, **kwargs):
        response = Airports.find(json.loads(request.body))
        return Response(response, status=status.HTTP_200_OK)

class ReviewsApiView(APIView):
    def post(self, request, *args, **kwargs):
        Client.send_review(json.loads(request.body))
        return Response(status=status.HTTP_200_OK)

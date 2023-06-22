from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.calculator.Client import Client
from api.Airports import Airports
from api.Authorize import Authorize
import json
import time
import environ

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

class AuthorizeApiView(APIView):
	def post(self, request, *args, **kwargs):
		response = Authorize.call(json.loads(request.body))
		print(response)
		return Response(response, status=status.HTTP_200_OK)

class UploadApiView(APIView):
	def post(self, request, *args, **kwargs):
		env = environ.Env()
		environ.Env.read_env()
		if request.headers["Authorization"].split(" ")[1] == env('ADMIN_TOKEN'):
			newFile = request.FILES['file']
			handle_uploaded_file(newFile)
			return Response(status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

def handle_uploaded_file(file):
	with open("base.csv", "wb+") as destination:
		for chunk in file.chunks():
			destination.write(chunk)

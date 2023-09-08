from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import json
import environ
from ..models import CharterHistory
from ..serializers import CharterHistorySerializer
from django.forms.models import model_to_dict

class ChartersHistoryApiView(APIView):
  serializer_class = CharterHistorySerializer

  authentication_classes = []
  permission_classes = []
  def post(self, request, *args, **kwargs):
    env = environ.Env()
    environ.Env.read_env()
    params = json.loads(request.body)
    if request.headers["Authorization"].split(" ")[1] == env('ADMIN_TOKEN'):
      charter_history = CharterHistory(
        number_of_flights=params.get("number_of_flights"),
        departure_city=params.get("departure_city"),
        arrival_city=params.get("arrival_city"),
      )
      charter_history.save()
      return Response(status=status.HTTP_200_OK)
    else:
      return Response(status=status.HTTP_401_UNAUTHORIZED)

  authentication_classes = []
  permission_classes = []
  def get(self, request, *args, **kwargs):
    histories = CharterHistory.objects.all()
    resp = map(
      lambda hist: {
        'number_of_flights': hist.number_of_flights,
        'departure_city': hist.departure_city,
        'arrival_city': hist.arrival_city,
        'id': hist.id
      },
      list(histories)
    )
    return Response(resp, status=status.HTTP_200_OK)

  def put(self, request, id, *args, **kwargs):
    # try:
      params = json.loads(request.body)
      try:
        charter_history = CharterHistory.objects.get(id=id)
      except:
        return Response(status=status.HTTP_404_NOT_FOUND)
      if params.get("number_of_flights"):
        charter_history.number_of_flights = params.get("number_of_flights")
      if params.get("departure_city"):
        charter_history.departure_city = params.get("departure_city")
      if params.get("arrival_city"):
        charter_history.arrival_city = params.get("arrival_city")
      charter_history.save()

      return Response(
        {
          'id': charter_history.id,
          'number_of_flights': charter_history.number_of_flights,
          'departure_city': charter_history.departure_city,
          'arrival_city': charter_history.arrival_city,
        },
        status=status.HTTP_200_OK
      )
    # except:
    #   return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  def delete(self, request, id, *args, **kwargs):
    try:
      charter_history = CharterHistory.objects.get(id=id)
    except:
      return Response(status=status.HTTP_404_NOT_FOUND)
    try:
      charter_history.delete()
      return Response(
        {
          'number_of_flights': charter_history.number_of_flights,
          'departure_city': charter_history.departure_city,
          'arrival_city': charter_history.arrival_city,
        },
        status=status.HTTP_200_OK
      )
    except:
      return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

  
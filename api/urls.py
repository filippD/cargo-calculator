from django.urls import path
from .views import CalculateApiView, RequestsApiView, AirportsApiView

urlpatterns = [
    path('calculate', CalculateApiView.as_view()),
    path('requests', RequestsApiView.as_view()),
    path('airports', AirportsApiView.as_view()),
]

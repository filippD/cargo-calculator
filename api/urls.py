from django.urls import path
from .views import CalculateApiView, RequestsApiView

urlpatterns = [
    path('calculate', CalculateApiView.as_view()),
    path('requests', RequestsApiView.as_view()),
]

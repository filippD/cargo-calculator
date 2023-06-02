from django.urls import path
from .views import CalculateApiView, RequestsApiView, AirportsApiView, ReviewsApiView, AuthorizeApiView, UploadApiView

urlpatterns = [
    path('calculate', CalculateApiView.as_view()),
    path('requests', RequestsApiView.as_view()),
    path('airports', AirportsApiView.as_view()),
    path('review', ReviewsApiView.as_view()),
    path('authorize', AuthorizeApiView.as_view()),
    path('upload', UploadApiView.as_view()),
]

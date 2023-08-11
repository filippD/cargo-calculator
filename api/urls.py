from django.urls import path
from .views import CalculateApiView, RequestsApiView, AirportsApiView, ReviewsApiView, AuthorizeApiView, UploadApiView, LoginApiView, UserApiView, SignUpApiView, LogoutApiView, SessionsApiView, RequestPaymentApiView, UpdateToPremiumApiView, ModifyPaymentEmailApiView

urlpatterns = [
    path('calculate', CalculateApiView.as_view()),
    path('requests', RequestsApiView.as_view()),
    path('airports', AirportsApiView.as_view()),
    path('review', ReviewsApiView.as_view()),
    path('authorize', AuthorizeApiView.as_view()),
    path('upload', UploadApiView.as_view()),
    path('login', LoginApiView.as_view()),
    path('user', UserApiView.as_view()),
    path('signup', SignUpApiView.as_view()),
    path('logout', LogoutApiView.as_view()),
    path('sessions', SessionsApiView.as_view()),
    path('payment_request', RequestPaymentApiView.as_view()),
    path('update_to_premium', UpdateToPremiumApiView.as_view()),
    path('modify_payment_email', ModifyPaymentEmailApiView.as_view()),
]

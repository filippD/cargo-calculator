from django.urls import path
from .views_old import CalculateApiView, RequestsApiView, AirportsApiView, ReviewsApiView, AuthorizeApiView, UploadApiView, LoginApiView, UserApiView, SignUpApiView, LogoutApiView, SessionsApiView, RequestPaymentApiView, UpdateToPremiumApiView, ModifyPaymentEmailApiView, CharterCompanyApiView
from api.views.CharterHistoriesView import ChartersHistoryApiView
from api.views.AuctionsGetApiView import AuctionsGetApiView
from api.views.AuctionsIndexApiView import AuctionsIndexApiView
from api.views.AuctionsCreateApiView import AuctionsCreateApiView
from api.views.AuctionsExpireApiView import AuctionsExpireApiView
from django.contrib import admin

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
    path('charter_histories', ChartersHistoryApiView.as_view()),
    path('charter_histories/<int:id>/', ChartersHistoryApiView.as_view()),
    path('charter_companies/<charter_id>/', CharterCompanyApiView.as_view()),
    path('auctions/<auction_id>/', AuctionsGetApiView.as_view()),
    path('auctions/', AuctionsIndexApiView.as_view()),
    path('auctions/create', AuctionsCreateApiView.as_view()),
    path('auctions/<auction_id>/expire', AuctionsExpireApiView.as_view()),
    path("admin/", admin.site.urls),
]

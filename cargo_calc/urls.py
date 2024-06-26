from django.urls import path
from django.urls import path, include
from api import urls as api_urls
from rest_framework_simplejwt import views as jwt_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
   path('api/', include(api_urls)),
   path('token/',
      jwt_views.TokenObtainPairView.as_view(), 
      name ='token_obtain_pair'
   ),
   path('token/refresh/',
      jwt_views.TokenRefreshView.as_view(), 
      name ='token_refresh')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

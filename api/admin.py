from django.contrib import admin
from .models import User, CharterHistory

# Register your models here.
admin.site.register(User)
admin.site.register(CharterHistory)
STATIC_URL = '/static/'
STATICFILES_DIRS=[
    os.path.join(BASE_DIR,'static')
]
STATIC_ROOT=os.path.join(BASE_DIR,'assests') 
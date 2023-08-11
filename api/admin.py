from django.contrib import admin
from .models import User, UserSession

# Register your models here.
admin.site.register(User)
admin.site.register(UserSession)

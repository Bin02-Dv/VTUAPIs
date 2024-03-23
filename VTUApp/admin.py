from django.contrib import admin

from .models import AuthApiModel, APIKey

# Register your models here.

admin.site.register(AuthApiModel)
admin.site.register(APIKey)

from django.contrib import admin

from .models import Transaction, APIKey, AuthApiModel

# Register your models here.

admin.site.register(Transaction)
admin.site.register(APIKey)
admin.site.register(AuthApiModel)

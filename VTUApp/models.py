from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.

class AuthApiModel(AbstractUser):
    name = models.CharField(max_length=225)
    email = models.CharField(max_length=225, unique=True)
    username = None
    password = models.CharField(max_length=225)
    phone_number = models.CharField(max_length=225, unique=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class APIKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(AuthApiModel, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.key)

class Transaction(models.Model):
    user = models.ForeignKey(AuthApiModel, on_delete=models.CASCADE)
    email_user = models.CharField(max_length=225)
    service = models.CharField(max_length=225)
    message = models.TextField(max_length=225)
    status = models.CharField(max_length=225)

    def __str__(self):
        return self.user.email

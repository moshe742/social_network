from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    ip = models.GenericIPAddressField()
    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=2, null=True)
    region = models.CharField(max_length=200, null=True)
    signup_at_holiday = models.BooleanField(null=True)

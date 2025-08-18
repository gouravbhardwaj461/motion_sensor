from django.db import models
from django.contrib.auth.models import User

class ConnectedDevice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    device_ip = models.GenericIPAddressField()
    is_active = models.BooleanField(default=False)
    connected_at = models.DateTimeField(auto_now=True)


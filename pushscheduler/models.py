from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class FCMToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    fcmToken = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
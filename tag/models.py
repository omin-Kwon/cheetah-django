from django.db import models
from colorfield.fields import ColorField
from django.contrib.auth.models import User

# Create your models here.


class Tag(models.Model):
    title = models.CharField(max_length=200, null=True)
    color = ColorField(default="#FF0000")
    is_used = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title

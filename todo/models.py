from django.db import models
from goal.models import Goal

# Create your models here.


class Todo(models.Model):
    title = models.CharField(max_length=200, null=False)
    is_completed = models.BooleanField(default=False, blank=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.title

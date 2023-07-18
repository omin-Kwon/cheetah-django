from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=200, null=False)

    start_at = models.DateField(null=True, blank=True)
    finish_at = models.DateField(null=True, blank=True)
    update_at = models.DateField(null=True, blank=True)
    prev_update_at = models.DateField(null=True, blank=True)  # for backup

    estimated_time = models.FloatField(null=True, blank=True)
    residual_time = models.FloatField(null=True, blank=True)
    prev_residual_time = models.FloatField(null=True, blank=True)  # for backup
    cumulative_time = models.FloatField(null=True, blank=True)
    prev_cumulative_time = models.FloatField(null=True, blank=True)  # for backup

    progress_rate = models.FloatField(null=True, blank=True)
    prev_progress_rate = models.FloatField(null=True, blank=True)  # for backup
    is_scheduled = models.BooleanField(default=False, blank=True)
    is_completed = models.BooleanField(default=False, blank=True)

    avaliable_days = ArrayField(
        models.IntegerField(default=1), size=7, null=True, blank=True
    )
    exception_list = ArrayField(
        models.DateField(), size=30, null=True, blank=True
    )  # 일단 30으로 제한함.

    def __str__(self):
        return self.title

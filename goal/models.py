from django.db import models
from django.contrib.auth.models import User
from tag.models import Tag
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

    def __str__(self):
        return self.title

# class AvailableDays(models.Model): #월화수목금토일 중 언제 가능한지 알려주는 테이블
#     goal = models.OneToOneField(Goal, on_delete=models.CASCADE, null=False)
#     monday = models.BooleanField(default=True)
#     tuesday = models.BooleanField(default=True)
#     wednesday = models.BooleanField(default=True)
#     thursday = models.BooleanField(default=True)
#     friday = models.BooleanField(default=True)
#     saturday = models.BooleanField(default=True)
#     sunday = models.BooleanField(default=True)

class ImpossibleDates(models.Model): #각 목표별로 불가능한 날짜를 알려주는 테이블
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=False)
    date = models.DateField(null=True, blank=True)

class DailyHourOfGoals(models.Model): #각 유저가 목표별로 특정 날짜에 얼마만큼 공부를 했는지 알려주는 테이블
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=False)
    hour = models.FloatField()
    date = models.DateField()

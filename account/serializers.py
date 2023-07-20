from django.forms import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework.validators import UniqueValidator
from datetime import datetime, date
from django.db.models import Q
import calendar
from goal.models import DailyHourOfGoals
from rest_framework.serializers import SerializerMethodField
from django.utils import timezone
from django.db.models import Sum
from goal.serializers import DailyHourOfGoalsSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
    
    def validate(self, attrs):
        username = attrs.get('username', '')
        password = attrs.get('password', '')
        if not username:
            raise ValidationError({"detail": "[username] fields missing."})
        if not password:
            raise ValidationError({"detail": "[password] fields missing."})
        return attrs
    
class UserProfileSerializer(ModelSerializer):
    monthly_hour = SerializerMethodField() # 해당 월에 얼마만큼 공부했는지에 대한 값
    def get_monthly_hour(self, obj):
        now = datetime.now()
        first_day = date(now.year, now.month, 1)
        _, last_day_num = calendar.monthrange(now.year, now.month)
        last_day = date(now.year, now.month, last_day_num)
        monthly_data = DailyHourOfGoals.objects.filter(Q(user=obj.user) & Q(date__gte=first_day) & Q(date__lte=last_day))
        monthly_hour_sum = monthly_data.aggregate(hour_sum=Sum('hour'))['hour_sum'] or 0

        return monthly_hour_sum
    
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"

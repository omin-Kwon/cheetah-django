from django.forms import ValidationError
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework.validators import UniqueValidator

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
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserProfile
        fields = "__all__"

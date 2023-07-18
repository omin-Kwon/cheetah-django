from rest_framework.serializers import ModelSerializer

# from account.serializers import UserIdUsernameSerializer
# from tag.serializers import TagSerializer

from .models import Todo


class TodoSerializer(ModelSerializer):
    class Meta:
        model = Todo
        fields = "__all__"

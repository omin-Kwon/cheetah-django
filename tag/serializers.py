from rest_framework.serializers import ModelSerializer

# from account.serializers import UserIdUsernameSerializer
# from tag.serializers import TagSerializer

from .models import Tag


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

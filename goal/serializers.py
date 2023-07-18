from rest_framework.serializers import ModelSerializer

# from account.serializers import UserIdUsernameSerializer
# from tag.serializers import TagSerializer

from .models import Goal
from todo.serializers import TodoSerializer


class GoalSerializer(ModelSerializer):
    class Meta:
        model = Goal
        fields = "__all__"


class GoalwithTodoSerializer(ModelSerializer):
    todo_set = TodoSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = "__all__"

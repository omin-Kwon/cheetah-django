from rest_framework.serializers import ModelSerializer


from .models import Goal, ImpossibleDates, DailyHourOfGoals
from todo.serializers import TodoSerializer
from tag.serializers import TagSerializer


class ImpossibleDatesSerializer(ModelSerializer):
    many = True

    class Meta:
        model = ImpossibleDates
        fields = ["date"]


# class AvailableDaysSerializer(ModelSerializer):
#     class Meta:
#         model = AvailableDays
#         fields = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class GoalSerializer(ModelSerializer):
    impossibledates_set = ImpossibleDatesSerializer(many=True, read_only=True)

    # availabledays = AvailableDaysSerializer(required=False)
    class Meta:
        model = Goal
        fields = "__all__"


class GoalwithTodoSerializer(ModelSerializer):
    # availabledays = AvailableDaysSerializer(required=False)
    impossibledates_set = ImpossibleDatesSerializer(many=True, read_only=True)
    todo_set = TodoSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = "__all__"


class GoalwithDailyHourOfGoalsSerializer(ModelSerializer):
    tag = TagSerializer(many=False, read_only=True)

    class Meta:
        model = Goal
        fields = ["id", "title", "progress_rate", "finish_at", "update_at", "tag"]


class DailyHourOfGoalsSerializer(ModelSerializer):
    goal = GoalwithDailyHourOfGoalsSerializer()

    class Meta:
        model = DailyHourOfGoals
        fields = "__all__"

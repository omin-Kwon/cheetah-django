from rest_framework.serializers import ModelSerializer


from .models import Goal, ImpossibleDates, DailyHourOfGoals
from todo.serializers import TodoSerializer

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
    impossibledates_set = ImpossibleDatesSerializer(many=True, read_only = True)
    # availabledays = AvailableDaysSerializer(required=False)
    class Meta:
        model = Goal
        fields = "__all__"



class GoalwithTodoSerializer(ModelSerializer):
    # availabledays = AvailableDaysSerializer(required=False)
    impossibledates_set = ImpossibleDatesSerializer(many=True, read_only = True)
    todo_set = TodoSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = "__all__"


class DailyHourOfGoalsSerializer(ModelSerializer):
    class Meta:
        model = DailyHourOfGoals
        fields = "__all__"
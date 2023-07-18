from django.urls import path
from .views import GoalList, GoalDetail

app_name = "goal"
urlpatterns = [
    path("", GoalList.as_view(), name="goal_list"),  # 전체 목표 리스트
    path("<int:goal_id>/", GoalDetail.as_view(), name="goal_detail"),  # 목표 상세
]

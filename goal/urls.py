from django.urls import path
from .views import GoalList, GoalDetail, ImpossibleDatesOfGoal

app_name = "goal"
urlpatterns = [
    path("", GoalList.as_view(), name="goal_list"),  # 전체 목표 리스트
    path("<int:goal_id>/", GoalDetail.as_view(), name="goal_detail"),  # 목표 상세
    path("impossibledates/<int:goal_id>/", ImpossibleDatesOfGoal.as_view(), name="impossibledates"),  #목표별 불가능한 날짜

]

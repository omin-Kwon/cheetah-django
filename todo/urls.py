from django.urls import path
from .views import TodoList, TodoDetail

app_name = "todo"
urlpatterns = [
    path("", TodoList.as_view(), name="todo_set"),  # 목표에 해당하는 todo 리스트
    path("<int:todo_id>/", TodoDetail.as_view(), name="todo_detail"),  # todo 수정, 삭제
]

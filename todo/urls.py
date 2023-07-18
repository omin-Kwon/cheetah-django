from django.urls import path
from .views import TodoList

app_name = "todo"
urlpatterns = [
    path("", TodoList.as_view(), name="todo_list"),  # 목표에 해당하는 todo 리스트
]

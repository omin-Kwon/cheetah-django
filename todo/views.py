from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Todo
from .serializers import TodoSerializer


class TodoList(APIView):
    def post(self, request):
        title = request.data.get("title", None)
        is_completed = request.data.get("is_completed", None)
        goal_id = request.data.get("goal_id", None)

        if not title or not is_completed or not goal_id:
            return Response("필수 입력값이 없습니다.", status=status.HTTP_400_BAD_REQUEST)

        todo = Todo.objects.create(
            title=title, is_completed=is_completed, goal_id=goal_id
        )
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        todo_id = request.query_params.get("todo_id", None)
        todo = Todo.objects.get(id=todo_id)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

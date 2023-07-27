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
        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)
        title = request.data.get("title", None)
        is_completed = request.data.get("is_completed", None)
        goal_id = request.data.get("goal_id", None)

        if title == None or is_completed == None or goal_id == None:
            return Response("필수 입력값이 없습니다.", status=status.HTTP_400_BAD_REQUEST)

        todo = Todo.objects.create(
            title=title, is_completed=is_completed, goal_id=goal_id
        )
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)
        goal = request.query_params.get("goal", None)
        if goal is not None:
            todo = Todo.objects.filter(goal_id=goal)
        else:
            todo = Todo.objects.all()
        serializer = TodoSerializer(todo, many=True)
        return Response(serializer.data)


class TodoDetail(APIView):
    def patch(self, request, todo_id):
        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)
        todo = Todo.objects.get(id=todo_id)
        serializer = TodoSerializer(todo, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, todo_id):
        try:
            todo = Todo.objects.get(id=todo_id)
        except Todo.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.shortcuts import render

# Create your views here.

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Tag
from .serializers import TagSerializer


class TagList(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)
        filtered_tags = request.query_params.get(
            "filtered_tags", None
        )  # 눈깔 킨 것만 보여주는 경우 true. 아니면 false
        if filtered_tags is not None:
            tags = Tag.objects.filter(is_used=True, user=request.user)
        else:
            tags = Tag.objects.filter(user=request.user)
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        title = request.data.get("title", None)
        color = request.data.get("color", None)
        is_used = request.data.get("is_used", None)

        if not user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)

        if title == None or color == None or is_used == None:
            return Response("필수 입력값이 없습니다.", status=status.HTTP_400_BAD_REQUEST)

        tag = Tag.objects.create(title=title, color=color, is_used=is_used, user=user)
        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagDetail(APIView):
    def get(self, request, tag_id):
        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)
        tag = Tag.objects.get(id=tag_id, user=request.user)
        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, tag_id):
        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)
        tags = Tag.objects.get(id=tag_id)
        serializer = TagSerializer(tags, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, tag_id):
        if not request.user.is_authenticated:
            return Response("로그인이 필요합니다.", status=status.HTTP_401_UNAUTHORIZED)
        tag = Tag.objects.get(id=tag_id)
        # 연관된 goal 까지 같이 삭제한다.
        tag.goal_set.all().delete()
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

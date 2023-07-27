from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ParseError
from .models import FCMToken

# Create your views here.
class FCMTokenDetail(APIView):
    def get(self, request):  # 특정 목표의 불가능한 날짜 얻기. 그냥 해당 목표에 대한 모든 정보 담고 있음.
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            token = FCMToken.objects.get(user=request.user)
        except ObjectDoesNotExist:
            raise NotFound("token not found.")
        return Response({"token": token}, status=status.HTTP_200_OK)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            print(request.user)
            print(request.data["token"])
            if FCMToken.objects.filter(user=request.user).exists():
                FCMToken.objects.update(user = request.user, fcmToken = request.data["token"])
            else:
                FCMToken.objects.create(
                user = request.user,
                fcmToken = request.data["token"]
            )
        except (ValueError, KeyError):
            raise ParseError(
                "Invalid date format. Date should be in the format 'YYYY-MM-DD'."
            )
        except Exception as e:
            raise ParseError(str(e))
        
        return Response({"detail": "Success"}, status=status.HTTP_201_CREATED)
    def delete(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials not provided"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        FCMToken.objects.filter(user = request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import UserProfile, AuthSMS
from .serializers import UserSerializer, UserProfileSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from datetime import timedelta, date
from pushscheduler.models import FCMToken


import sys
import os
import hashlib
import hmac
import base64
import requests
import time
import json

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# Create your views here.


def set_token_on_response_cookie(user: User, autologin=False) -> Response:
    token = RefreshToken.for_user(user)
    if autologin == True:
        token.set_exp(lifetime=timedelta(days=30))
    user_profile = UserProfile.objects.get(user=user)
    user_profile_serializer = UserProfileSerializer(user_profile)
    res = Response(user_profile_serializer.data, status=status.HTTP_201_CREATED)
    res.set_cookie("refresh_token", value=str(token), domain=".cheetah-do.xyz")
    res.set_cookie(
        "access_token", value=str(token.access_token), domain=".cheetah-do.xyz"
    )

    return res


class IdDuplicationCheck(APIView):  # 회원가입시 아이디 중복 체크
    def get(self, request):
        username = request.query_params["username"]
        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "중복된 아이디입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_200_OK)


class SMSAuth(APIView):  # 전화번호 인증. post 요청시 문자 발송, get 요청시 인증번호 확인
    def post(self, request):
        try:
            p_num = request.data.get("phone_num")

        except KeyError:
            return Response(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            AuthSMS.objects.update_or_create(phone_num=p_num)
            return Response({"message": "OK"})

    def get(self, request):
        try:
            p_num = request.query_params["phone_num"]
            a_num = request.query_params["auth_number"]
        except KeyError:
            return Response(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            identification_result = AuthSMS.check_auth_number(p_num=p_num, a_num=a_num)
            if identification_result == True:
                return Response(
                    {"message": "OK", "identification_result": identification_result}
                )
            if identification_result == False:
                return Response(
                    {"message": "전화번호 인증에 실패하였습니다."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )


class Signup(APIView):  # 회원 가입
    def post(self, request):
        # if 'nickname' not in request.data:
        #     return Response(data={"message": "nickname이 입력되지 않았습니다."}, status = status.HTTP_400_BAD_REQUEST)
        # if 'phone_num' not in request.data:
        #     return Response(data={"message": "phone_num이 입력되지 않았습니다."}, status = status.HTTP_400_BAD_REQUEST)
        default_max_speed = 6

        nickname = request.data.get("nickname")
        phone_num = request.data.get("phone_num")
        if "max_speed" in request.data:
            max_speed = request.data["max_speed"]
        else:
            max_speed = default_max_speed

        # if UserProfile.objects.filter(phone_num=phone_num).exists():
        #     return Response(
        #         {"detail": "해당 전화번호로 가입한 계정이 이미 존재합니다."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.save()
            user.set_password(request.data.get("password"))
            user.save()

        user_profile = UserProfile.objects.create(
            user=user, nickname=nickname, phone_num=phone_num, max_speed=max_speed
        )

        return set_token_on_response_cookie(user)


class FindId(APIView):  # 아이디 찾기
    def get(self, request):
        phone_num = request.query_params["phone_num"]

        if UserProfile.objects.filter(phone_num=phone_num).exists():
            user_profile = UserProfile.objects.get(phone_num=phone_num)
            user = user_profile.user
            username = user.username
            return Response({"username": username}, status=status.HTTP_200_OK)
        else:
            return Response({"username": "NOT FOUND"}, status=status.HTTP_404_NOT_FOUND)


class FindPassword(APIView):  # 비밀번호 찾기
    def get(self, request):
        phone_num = request.query_params["phone_num"]

        if UserProfile.objects.filter(phone_num=phone_num).exists():
            user_profile = UserProfile.objects.get(phone_num=phone_num)
            user = user_profile.user
            username = user.username
            if username == request.query_params["username"]:
                return Response({"detail": "OK"}, status=status.HTTP_200_OK)
        else:
            return Response({"username": "NOT FOUND"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        username = request.data.get("username")
        new_password = request.data.get("new_password")
        try:
            user = User.objects.get(username=username)
            # user.password = new_password
            user.set_password(new_password)
            user.save()
            print(user.password)
        except KeyError:
            return Response(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response({"message": "OK"}, status=status.HTTP_200_OK)


class Signin(APIView):  # 회원가입
    def post(self, request):
        try:
            user = User.objects.get(
                username=request.data["username"],
            )
            if not user.check_password(request.data["password"]):
                raise ValueError("Invalid password")
            auto_login = request.data["autologin"]
        except:
            return Response(
                {"detail": "아이디 또는 비밀번호를 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST
            )
        return set_token_on_response_cookie(user, auto_login)


class Logout(APIView):  # 로그아웃
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인 후 다시 시도해주세요."}, status=status.HTTP_401_UNAUTHORIZED
            )
        RefreshToken(request.data["refresh"]).blacklist()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access_token", domain=".cheetah-do.xyz")
        response.delete_cookie("refresh_token", domain=".cheetah-do.xyz")
        FCMToken.objects.filter(user=request.user).delete()

        return response


class TokenRefresh(APIView):  # 액세스 토큰 재발급
    def post(self, request):
        refresh_token = request.data["refresh"]
        try:
            print("hello")
            RefreshToken(refresh_token).verify()
            print("hi")
        except:
            return Response(
                {"detail": "로그인 후 다시 시도해주세요."}, status=status.HTTP_401_UNAUTHORIZED
            )
        new_access_token = str(RefreshToken(refresh_token).access_token)
        response = Response({"detail": "token refreshed"}, status=status.HTTP_200_OK)
        response.set_cookie(
            "access_token", value=str(new_access_token), domain=".cheetah-do.xyz"
        )
        return response


class MyPage(APIView):  # 마이페이지
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인 후 다시 시도해주세요."}, status=status.HTTP_401_UNAUTHORIZED
            )
        user_profile = UserProfile.objects.get(user=request.user)
        return Response(
            UserProfileSerializer(user_profile).data, status=status.HTTP_200_OK
        )

    def patch(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인 후 다시 시도해주세요."}, status=status.HTTP_401_UNAUTHORIZED
            )
        user = request.user
        user_profile = UserProfile.objects.get(user=user)
        try:
            user_profile.max_speed = request.data["max_speed"]
            user_profile.nickname = request.data["nickname"]
            user_profile.save()
        except:
            return Response(
                {"message": "Bad Request"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"detail": "userProfile changed"}, status=status.HTTP_200_OK)

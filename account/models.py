from django.db import models
from django.contrib.auth.models import User

import uuid
import sys
import os
import hashlib
import hmac
import base64
import requests
import time
import json
from random import randint
from django.http import HttpResponse
import datetime
from django.utils import timezone

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# Create your models here.

# class CustomUser(AbstractUser):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=10, blank=False)
    phone_num = models.CharField(max_length=11, blank=False)
    max_speed = models.IntegerField(default=6)
    level = models.IntegerField(default=1)
    exp = models.FloatField(default=0)

    def __str__(self):
        return f"id={self.id}, user_id={self.user.id}, nickname={self.nickname}, phone_num={self.phone_num}, max_speed={self.max_speed}, level={self.level}, exp={self.exp}"


class TimeStampedModel(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class AuthSMS(TimeStampedModel):
    phone_num = models.CharField(max_length=11, blank=False, primary_key=True)
    auth_number = models.IntegerField(blank=False)

    def save(self, *args, **kwargs):
        self.auth_number = randint(1000, 10000)
        AuthSMS.objects.filter(phone_num=self.phone_num).update(
            auth_number=self.auth_number
        )
        super().save(*args, **kwargs)
        self.send_sms()

    def make_signature(self, message):
        secret_key = os.getenv(
            "NCLOUD_SCRET_KEY"
        )  # secret key (from portal or Sub Account)
        secret_key = bytes(str(secret_key), "UTF-8")
        signingKey = base64.b64encode(
            hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
        )
        return signingKey

    def send_sms(self):
        URI = "/sms/v2/services/{}/messages".format(os.getenv("SERVICE_ID"))
        API_URL = "https://sens.apigw.ntruss.com{}".format(URI)
        timestamp = str(int(time.time() * 1000))
        ACCESS_KEY = os.getenv("NCLOUD_ACCESS_KEY")

        message = "POST" + " " + URI + "\n" + timestamp + "\n" + str(ACCESS_KEY)
        message = bytes(message, "UTF-8")

        SIGNATURE = self.make_signature(message)

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "x-ncp-apigw-timestamp": timestamp,
            "x-ncp-iam-access-key": ACCESS_KEY,
            "x-ncp-apigw-signature-v2": SIGNATURE,
        }

        body = {
            "type": "SMS",
            "contentType": "COMM",
            "countryCode": "82",
            "from": os.getenv("SEND_PHONE_NUM"),
            "content": "[테스트] 인증 번호 [{}]를 입력해주세요.".format(self.auth_number),
            "messages": [{"to": self.phone_num}],
        }
        res = requests.post(API_URL, data=json.dumps(body), headers=headers)
        print(URI)
        print(API_URL)
        print(headers)
        print(body)
        print(res.status_code)
        return HttpResponse(res.status_code)

    @classmethod
    def check_auth_number(cls, p_num, a_num):
        time_limit = timezone.now() - datetime.timedelta(minutes=5)
        result = cls.objects.filter(
            phone_num=p_num, auth_number=a_num, modified_time__gte=time_limit
        )
        if result:
            return True
        return False

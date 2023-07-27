from django.contrib import admin
from django.urls import path, include
from .views import FCMTokenDetail
app_name = 'pushscheduler'
urlpatterns = [
    path("", FCMTokenDetail.as_view()),



]
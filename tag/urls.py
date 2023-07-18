from django.urls import path
from .views import TagList, TagDetail

app_name = "tag"
urlpatterns = [
    path("", TagList.as_view(), name="tag_list"),  # 전체 태그 리스트
    path("<int:tag_id>/", TagDetail.as_view(), name="tag_detail"),  # 태그 상세
]

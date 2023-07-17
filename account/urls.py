from django.urls import path
from .views import Signup, Signin, IdDuplicationCheck, SMSAuth, FindId, FindPassword, Logout, TokenRefresh, MyPage


app_name = 'account'
urlpatterns = [
    path("idduplicationcheck/", IdDuplicationCheck.as_view()),
    path("signup/", Signup.as_view()),
    path("signin/", Signin.as_view()),
    path("smsauth/", SMSAuth.as_view()),
    path("findid/", FindId.as_view()),
    path("findpassword/", FindPassword.as_view()),
    path("logout/", Logout.as_view()),
    path("refresh/", TokenRefresh.as_view()),
    path("mypage/", MyPage.as_view())


]
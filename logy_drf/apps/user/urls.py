from django.urls import path, re_path
from rest_framework.views import APIView
from rest_framework.response import Response
from . import views

class Test(APIView):
    def get(self,request):
        return Response('ok')

urlpatterns = [
    path('test/',Test.as_view()),
    path('login', views.LoginAPIView.as_view()),
    path('login/mobile', views.LoginMobileAPIView.as_view()),
    path('register', views.RegisterAPIView.as_view()),
    path('sms', views.SMSAPIView.as_view()),
    path('mobile', views.MobileAPIView.as_view()),
    path('condition',views.Condition.as_view()),
    path('word', views.Word.as_view()),
    path('movie', views.Movie.as_view()),
    path('order', views.Order.as_view()),
    path('order1', views.Order1.as_view()),
    path('order2', views.Order2.as_view()),
    path('add_order', views.Add_Order.as_view()),
    re_path('^change_order/(?P<id>\d+)$', views.Change_Order.as_view()),
    re_path('^change_user/(?P<id>\d+)$', views.Change_User.as_view()),
    # re_path('^user/(?P<id>\d+)$', views.User.as_view()),
    path('pay', views.PayAPIView.as_view()),

]
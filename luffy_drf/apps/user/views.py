from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from .paginations import OrderPageNumberPagination, CourseLimitOffsetPagination, CourseCursorPagination
from utils.response import APIResponse
from . import models,serializers,throttles
from django.core.cache import cache
from django.conf import settings
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from libs import tx_sms
import datetime,random
import re
# Create your views here.

class LoginAPIView(APIView):
    def post(self,request,*args,**kwargs):
        # print(123)
        serializer=serializers.LoginModelSerializer(data=request.data)
        # print(456)
        if serializer.is_valid():
            return APIResponse(data={
                'username': serializer.user.username,
                'token': serializer.token,
                'nice_name':serializer.user.nice_name,
                'id':serializer.user.id,
                'money':serializer.user.money,
            })
        return APIResponse(1, 'failed', data=serializer.errors, http_status=400)

class LoginMobileAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginMobileSerializer(data=request.data)
        if serializer.is_valid():
            return APIResponse(data={
                'username': serializer.user.username,
                'token': serializer.token,
                'nice_name':serializer.user.nice_name,
                'id': serializer.user.id
            })
        return APIResponse(1, 'failed', data=serializer.errors, http_status=400)

class MobileAPIView(APIView):
    def post(self, request, *args, **kwargs):
        mobile = request.data.get('mobile')

        # 不管前台处不处理格式校验，后台一定需要校验
        if not (mobile and re.match(r'^1[3-9][0-9]{9}$', mobile)):
            return APIResponse(2, '手机号格式有误')

        try:
            # 已经注册了
            models.User.objects.get(mobile=mobile)
            return APIResponse(1, '手机已注册')
        except:
            # 没有注册过
            return APIResponse(0, '手机未注册')

# 手机验证码注册
class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = serializers.RegisterMobileSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return APIResponse(0, '注册成功', data={
                'username': obj.username,
                'nice_name' : obj.nice_name,
                'mobile': obj.mobile,
                'email': obj.email,
            })
        return APIResponse(1, '注册失败', data=serializer.errors, http_status=400)

# 发送短信
class SMSAPIView(APIView):
    throttle_classes = [throttles.SMSRateThrottle]
    def post(self, request, *args, **kwargs):
        # print(123)
        mobile = request.data.get('mobile')
        if not (mobile and re.match(r'^1[3-9][0-9]{9}$', mobile)):
            return APIResponse(2, '手机号格式有误')
        # 获取验证码
        code = tx_sms.get_code()
        # 发送短信
        result = tx_sms.send_sms(mobile, code, settings.SMS_EXP // 60)
        # 服务器缓存验证码
        # print(456)
        if not result:
            return APIResponse(1, '发送验证码失败')
        cache.set(settings.SMS_CACHE_KEY % mobile, code, settings.SMS_EXP)
        # 校验发送的验证码与缓存的验证码是否一致
        # print(789)
        # print('>>>> %s - %s <<<<' % (code, cache.get('sms_%s' % mobile)))
        return APIResponse(0, '发送验证码成功')

class Condition(APIView):
    def get(self, request, *args, **kwargs):
        category_query = models.Category.objects.all()
        # 完成序列化
        category_list_data = serializers.CategoryModelSerializer(category_query, many=True).data
        place_query = models.Place.objects.filter(parent_id=False)
        place_list_data = serializers.PlaceModelSerializer(place_query, many=True).data
        place_query1 = models.Place.objects.filter(parent_id=1)
        place_list_data1 = serializers.PlaceModelSerializer(place_query1, many=True).data
        place_query2 = models.Place.objects.filter(parent_id=2)
        place_list_data2 = serializers.PlaceModelSerializer(place_query2, many=True).data
        place_query4 = models.Place.objects.filter(parent_id=4)
        place_list_data4 = serializers.PlaceModelSerializer(place_query4, many=True).data
        # for i in place_list_data1:
        #     print(i)
        return APIResponse(data={
            'category': category_list_data,
            'place': place_list_data,
            'place1': place_list_data1,
            'place2': place_list_data2,
            'place4': place_list_data4,

        })

# class Order(APIView):
#     def get(self, request, *args, **kwargs):
#         # pk = kwargs.get('pk')
#         # if pk:
#         #     user_obj = models.User.objects.filter(pk=pk).first()
#         #     if not user_obj:
#         #         return Response({
#         #             'status': 1,
#         #             'msg': '单查 error'
#         #         })
#         #     # 完成序列化
#         #     user_data = serializers.UserModelSerializer(user_obj, many=False).data
#         #     return Response({
#         #         'status': 0,
#         #         'msg': '单查 ok',
#         #         'results': user_data
#         #     })
#
#         # 群查
#         order_query = models.Order.objects.all()
#         # 完成序列化
#         order_list_data = serializers.OrderModelSerializer(order_query, many=True).data
#         # for i in order_query:
#         #     print(i.place_name)
#         for i in order_list_data:
#             print(i)
#         return APIResponse(data={
#             'order':order_list_data
#         })

class Order(ListAPIView):
    queryset = models.Order.objects.all()
    order_all=queryset.count()
    serializer_class = serializers.OrderModelSerializer
    pagination_class = OrderPageNumberPagination
    ordering_fields = ['price', 'id', 'end']
    filter_fields = ['place', 'status']
    def get(self, request, *args, **kwargs):
        # orders = models.Order.objects.all()
        # order_all = orders.count()
        response = self.list(request, *args, **kwargs)
        print(response.data)
        # response.data['order_all']=order_all
        # print(order_all)
        return response

class Order1(ListAPIView):

    queryset = models.Order.objects.all()
    order_all=queryset.count()
    serializer_class = serializers.OrderModelSerializer
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields = ['price', 'id', 'end']
    search_fields = ['start', 'end']
    filter_fields = ['place','status','id']
    pagination_class = OrderPageNumberPagination
    # def get(self, request, *args, **kwargs):
    #     response = self.list(request, *args, **kwargs)
    #     # orders = models.Order.objects.all()
    #     # order_all = orders.count()
    #     print(response.data)
    #     # response.data['order_all']=order_all
    #     # print(order_all)
    #     return response

class Order2(ListAPIView):

    queryset = models.Order.objects.all()
    order_all=queryset.count()
    serializer_class = serializers.OrderModelSerializer
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields = ['price', 'id', 'end']
    search_fields = ['start', 'end']
    filter_fields = ['place','status','up_user','down_user']


class Add_Order(APIView):
    def post(self, request, *args, **kwargs):
        request_data = request.data
        request_data['create_time']=datetime.datetime.now()
        request_data['get_time']=datetime.datetime.now()
        print(request_data)
        order_ser = serializers.OrderModelSerializer(data=request_data)
        # 校验失败，直接抛异常，反馈异常信息给前台，只要校验通过，代码才会往下执行
        result = order_ser.is_valid()
        print(result)
        if result:

            order_ser.save()
            return APIResponse()
        else:
            # 校验失败，返回错误信息
            return APIResponse(1, 'failed', data=order_ser.errors, http_status=400)

class Change_Order(APIView):
    def patch(self, request, *args, **kwargs):
        request_data = request.data
        print(request_data)
        pk = kwargs.get('id')
        order_obj = models.Order.objects.filter(pk=pk).first()
        # 目的：将众多数据的校验交给序列化类来处理 - 让序列化类扮演反序列化角色，校验成功后，序列化类来帮你入库
        order_ser = serializers.OrderModelSerializer(instance=order_obj, data=request_data, partial=True)
        order_ser.is_valid(raise_exception=True)
        # 校验通过，完成数据的更新：要更新的目标，用来更新的新数据
        order_ser.save()

        return APIResponse()


from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
class PayAPIView(APIView):
    # authentication_classes = [JSONWebTokenAuthentication]
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = serializers.ChargeModelSerializer(data=request.data, context={'request': request})
        # 信息校验
        serializer.is_valid(raise_exception=True)
        # 订单入库
        serializer.save()
        # 返回一个支付链接
        return Response(serializer.pay_url)


class Change_User(APIView):
    def patch(self, request, *args, **kwargs):
        request_data = request.data
        print(request_data)
        pk = kwargs.get('id')
        user_obj = models.User.objects.filter(pk=pk).first()
        # 目的：将众多数据的校验交给序列化类来处理 - 让序列化类扮演反序列化角色，校验成功后，序列化类来帮你入库
        order_ser = serializers.UserModelSerializer(instance=user_obj, data=request_data, partial=True)
        order_ser.is_valid(raise_exception=True)
        # 校验通过，完成数据的更新：要更新的目标，用来更新的新数据
        order_ser.save()
        return APIResponse()


class Word(ListAPIView):

    queryset = models.Word.objects.all()
    # order_all = queryset.count()
    serializer_class = serializers.WordModelSerializer
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]

    filter_fields = ['id']


class Movie(ListAPIView):

    queryset = models.Movie.objects.all()
    # order_all = queryset.count()
    serializer_class = serializers.MovieModelSerializer
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]

    filter_fields = ['order']
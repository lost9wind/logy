from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from user import models
from django.core.cache import cache
from django.conf import settings
# from . import models
from libs.iPay import alipay, alipay_gateway
import re,time

class LoginModelSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    # re_pwd = serializers.CharField(min_length=8, max_length=16, write_only=True)
    # nice_name=serializers.CharField()

    class Meta:
        model = models.User
        fields = ['username', 'password']
        extra_kwargs = {
            # 'username': {
            #     'required': True,
            #     'min_length': 3,
            #     'max_length': 10,
            #     'error_messages': {
            #         'min_length': '用户名长度过短',
            #         'max_length': '用户名长度过长'
            #     }
            # },
            'password': {
                'required': True,  # 数据库有默认值或可以为空字段，required默认为False
                'min_length': 8,
                'max_length': 16,
                'error_messages': {
                    'min_length': '密码长度过短',
                    'max_length': '密码长度过长',
                }
            },
            # 'nice_name': {
            #     'required': True,
            #     'max_length': 10,
            #     'error_messages': {
            #         'max_length': '昵称长度过长'
            #     }
            # },
        }

    def validate(self, attrs):
        # password = attrs.get('password')
        # re_pwd = attrs.pop('re_pwd')
        # if password != re_pwd:
        #     raise serializers.ValidationError({'re_pwd': '两次密码不一致'})
        user = self._many_method_login(**attrs)

        # 签发token，并将user和token存放到序列化对象中
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        self.user = user
        self.token = token
        # self.nice_name = nice_name
        return attrs
    def _many_method_login(self, **attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if re.match(r'.*@.*', username):
            user = models.User.objects.filter(email=username).first()

        elif re.match(r'^1[3-9][0-9]{9}$', username):
            user = models.User.objects.filter(mobile=username).first()
        else:
            user = models.User.objects.filter(username=username).first()

        if not user:
            raise serializers.ValidationError({'username': '账号有误'})

        if not user.check_password(password):
            raise serializers.ValidationError({'password': '密码有误'})

        return user

# 手机验证码登录
class LoginMobileSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(write_only=True, min_length=11, max_length=11)
    code = serializers.CharField(write_only=True, min_length=4, max_length=4)
    class Meta:
        model = models.User
        fields = ('mobile', 'code')

    def validate_mobile(self, value):
        if re.match(r'^1[3-9][0-9]{9}$', value):
            return value
        raise serializers.ValidationError('手机号格式有误')

    def validate_code(self, value):
        try:
            int(value)
            return value
        except:
            raise serializers.ValidationError('验证码格式有误')

    # 校验user，签发token，保存到serializer
    def validate(self, attrs):
        user = self._get_user(**attrs)

        # 签发token，并将user和token存放到序列化对象中
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        self.user = user
        self.token = token

        return attrs

    # 获取用户
    def _get_user(self, **attrs):
        mobile = attrs.get('mobile')
        code = attrs.get('code')
        user = models.User.objects.filter(mobile=mobile).first()
        if not user:
            raise serializers.ValidationError({'mobile': '该手机号未注册'})

        # 拿到之前缓存的验证码
        old_code = cache.get(settings.SMS_CACHE_KEY % mobile)
        if code != old_code:
            raise serializers.ValidationError({'code': '验证码有误'})
        # 为了保证验证码安全，验证码验证成功后，失效
        # cache.set(settings.SMS_CACHE_KEY % mobile, '0000', 0)
        return user

# 手机验证码注册
class RegisterMobileSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, min_length=4, max_length=4)
    class Meta:
        model = models.User
        fields = ('username', 'nice_name', 'mobile', 'code', 'password')
        extra_kwargs = {
            'username': {
                'required': True,
                'min_length': 3,
                'max_length': 10,
                'error_messages': {
                    'min_length': '用户名长度过短',
                    'max_length': '用户名长度过长'
                }
            },
            'mobile': {
                'min_length': 11,
                'max_length': 11,
                'error_messages': {
                    'min_length': '手机格式错误',
                    'max_length': '手机格式错误'
                }
            },
            'password': {
                'min_length': 8,
                'max_length': 16,
                'write_only' : True,
                'error_messages': {
                    'min_length': '密码长度过短',
                    'max_length': '密码长度过长'
                }
            },
            'nice_name': {
                'required': True,
                'max_length': 10,
                'error_messages': {
                    'max_length': '昵称长度过长'
                }
            },
        }

    def validate_mobile(self, value):
        if re.match(r'^1[3-9][0-9]{9}$', value):
            return value
        raise serializers.ValidationError('手机号格式有误')

    def validate_code(self, value):
        try:
            int(value)
            return value
        except:
            raise serializers.ValidationError('验证码格式有误')

    def validate_password(self, value):
        # 密码不能包含或必须包含哪些字符
        return value

    # 拿出不入库的数据，塞入额外要入库的数据
    def validate(self, attrs):
        mobile = attrs.get('mobile')
        code = attrs.pop('code')
        old_code = cache.get(settings.SMS_CACHE_KEY % mobile)
        if code != old_code:
            raise serializers.ValidationError({'code': '验证码有误'})
        # cache.set(settings.SMS_CACHE_KEY % mobile, '0000', 0)  # 清除一次性验证码

        # attrs['username'] = mobile
        attrs['email'] = '%s@daidai.com' % mobile

        return attrs

    # User表必须重写create方法，才能操作密文密码
    def create(self, validated_data):
        return models.User.objects.create_user(**validated_data)


class CategoryModelSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField()
    class Meta:
        model = models.Category
        fields = '__all__'

class PlaceModelSerializer(ModelSerializer):
    place_name = serializers.CharField()
    class Meta:
        model = models.Place
        fields = '__all__'

class WordModelSerializer(ModelSerializer):

    class Meta:
        model = models.Word
        fields = '__all__'


class MovieModelSerializer(ModelSerializer):

    class Meta:
        model = models.Movie
        fields = ['name','intro','id','direction','order','image','like','collections_num','owner_name','owner']

class OrderModelSerializer(ModelSerializer):

    class Meta:
        model = models.Order
        fields = ['id', 'place','game_id','game_password', 'start', 'end', 'game_name', 'price', 'deposit', 'times', 'get_time', 'work',
                  'content', 'create_time', 'up_user', 'down_user', 'status', 'status_name', 'place_name',
                  'place_parent_name', 'up_user_name', 'down_user_name']

class UserModelSerializer(ModelSerializer):

    class Meta:
        model = models.User
        fields = ['id','username','password','icon','mobile','money','level','win_point','teacher','level_name']

#     def validate(self, attrs):
#         id = attrs.get('id')
#         user=models.User.objects.filter(pk=id).first()
#         self.user=user
#
#         return attrs

class ChargeModelSerializer(ModelSerializer):

    class Meta:
        model=models.Recharge
        fields=['id','method','num','user','method_name']

    def validate(self, attrs):
        num=attrs.pop('num')
        order_on = self._get_order_no()
        subject = attrs.get('method')
        print(num,subject)
        order_params = alipay.api_alipay_trade_page_pay(out_trade_no=order_on,
                                                        total_amount=float(num),
                                                        subject=subject,
                                                        return_url=settings.RETURN_URL,  # 同步回调的前台接口
                                                        notify_url=settings.NOTIFY_URL  # 异步回调的后台接口
                                                        )
        pay_url = alipay_gateway + order_params
        self.pay_url = pay_url
        attrs['trade_no'] = order_on
        attrs['num'] = num
        return attrs

    def _get_order_no(self):
        no = '%s' % time.time()
        return no.replace('.', '', 1)
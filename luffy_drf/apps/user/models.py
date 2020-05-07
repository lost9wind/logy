from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    # id = models.AutoField(primary_key=True)  # 用户id
    # username = models.CharField(max_length=50)  # 账号
    nice_name = models.CharField(max_length=50,null=True)  # 昵称
    # password = models.CharField(max_length=50)   # 密码
    mobile = models.CharField(max_length=11, unique=True,null=True)   #手机
    icon = models.ImageField(upload_to='icon', default='icon/default.png')  # 头像
    money = models.DecimalField(max_digits=15, decimal_places=2, default=0)  # 余额
    # creat_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    # update_time = models.DateTimeField(auto_now=True)  # 修改时间
    level_choices = ((0, '未申请打手审核'), (1, '黑铁'), (2, '青铜'), (3, '白银'), (4, '黄金'), (5, '白金'), (6, '钻石'), (7, '超凡大师'), (8, '傲世宗师'), (9, '最强王者'))
    level = models.SmallIntegerField(choices=level_choices, default=0)  # 打手等级
    win_point = models.IntegerField(default=0)  # 升级经验
    teacher = models.ForeignKey(to='User', to_field='id', related_name="User", on_delete=models.CASCADE,db_constraint=False, blank=True, null=True)  # 一对一教学

    @property
    def level_name(self):
        return self.get_level_display()

    class Meta:
        db_table = 'user'
        verbose_name = '用户表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

class Category(models.Model):
    id = models.AutoField(primary_key=True)		#分类id
    category_name = models.CharField(max_length=50)	#大/小段位
    parent=models.ForeignKey(to='Category', to_field='id', related_name="Category", on_delete=models.CASCADE, db_constraint=False,blank=True,null=True)	  #大段位
    p_order=models.IntegerField(default=0)		#展示顺序
    creat_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.category_name

class Place(models.Model):
    id = models.AutoField(primary_key=True)		#大区id
    place_name = models.CharField(max_length=50)		#服/区
    parent = models.ForeignKey(to='Place', to_field='id', related_name="Place", on_delete=models.CASCADE, db_constraint=False,blank=True,null=True)		#区
    p_order=models.IntegerField(default=0)		#展示顺序
    creat_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.place_name


class Order(models.Model):
    id = models.AutoField(primary_key=True)  # 订单id
    place = models.ForeignKey(to='Place', to_field='id', related_name="Order", on_delete=models.CASCADE,
                                 db_constraint=False)  # 大区
    start = models.CharField(max_length=50)  # 初始段位
    end = models.CharField(max_length=50)  # 结束段位
    game_name = models.CharField(max_length=100)  # 游戏角色名
    game_id = models.CharField(max_length=100,default=0)  #游戏账号
    game_password = models.CharField(max_length=100,default=0)    #游戏密码
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 订单价格
    deposit = models.DecimalField(max_digits=10, decimal_places=2)  # 押金
    times = models.IntegerField(default=0)  # 订单任务时间
    get_time = models.DateTimeField(auto_now_add=True, null=True)  # 接手时间
    work=models.CharField(max_length=100,default='单双排')   #标题
    content = models.TextField()  # 订单说明和要求
    create_time = models.DateTimeField(auto_now_add=True,null=True)  # 创建时间
    up_user = models.ForeignKey('User',related_name="uo_user",  on_delete=models.CASCADE,
                                 db_constraint=False,null=True)  # 上家
    down_user = models.ForeignKey('User',related_name="down_user",   on_delete=models.CASCADE,
                                 db_constraint=False,null=True)  # 下家
    status_choices = (
    (0, '未接手'), (1, '已接手'), (2, '申请完单'), (3, '已结算'), (4, '提交异常'), (5, '申请撤销'), (6, '已撤销'), (7, '客服介入'), (8, '介入撤销'),
    (9, '订单锁定'))
    status = models.SmallIntegerField(choices=status_choices, default=0)  # 订单状态

    @property
    def status_name(self):
        return self.get_status_display()

    @property
    def place_name(self):
        return self.place.place_name

    @property
    def place_parent_name(self):
        return self.place.parent.place_name

    @property
    def up_user_name(self):
        return self.up_user.nice_name

    @property
    def down_user_name(self):
        return self.down_user.nice_name


    def __str__(self):
        return self.id

class Comment(models.Model):
    id = models.AutoField(primary_key=True)		#评价id
    comment_name = models.CharField(max_length=100)	#评价内容
    count=models.IntegerField(default=1)   #评价数量
    user = models.ForeignKey(to='User', to_field='id', related_name="Comment", on_delete=models.CASCADE, db_constraint=False)	#被评价者
    creat_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.comment_name

class Images(models.Model):
    id=models.AutoField(primary_key=True)		#id
    img_name=models.CharField(max_length=30,default="0")	#名字
    image_url=models.ImageField(upload_to="../../media/img")		#地址
    creat_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.img_name


class Notice(models.Model):
    id=models.AutoField(primary_key=True)	#id
    title=models.CharField(max_length=50)	#标题
    desc=models.CharField(max_length=100)	#简介
    notice_content=models.TextField()		#内容
    creat_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title


class Word(models.Model):
    id=models.AutoField(primary_key=True)	#id
    person_name=models.CharField(max_length=50)		#英雄
    person_word=models.CharField(max_length=200)	#台词
    creat_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.person_name


class Recharge(models.Model):
    id = models.AutoField(primary_key=True)  # id
    method_choices = ((0, '充值'), (1, '取现'))
    method =models.SmallIntegerField(choices=method_choices, default=0)  # 订单状态
    num = models.DecimalField(max_digits=10, decimal_places=2)    #金额
    user=models.ForeignKey('User',related_name="recharge",  on_delete=models.CASCADE,
                                 db_constraint=False,null=True)  # 用户
    creat_time = models.DateTimeField(auto_now_add=True ,null=True,)
    update_time = models.DateTimeField(auto_now=True ,null=True,)
    trade_no = models.CharField(max_length=64, null=True, verbose_name="流水号")

    @property
    def method_name(self):
        return self.get_method_display()

    @property
    def user_name(self):
        return self.user.nice_name

    def __str__(self):
        return self.id


class Movie(models.Model):
    name = models.CharField(max_length=25, verbose_name='视频名称')
    intro = models.CharField(max_length=255, verbose_name='视频简介')
    direction = models.CharField(max_length=255, verbose_name='视频路径')
    order = models.IntegerField(verbose_name="展示顺序",default=0)
    image = models.ImageField(upload_to='movie_img', verbose_name='视频图片')
    # heat = models.IntegerField(verbose_name='电影热度')
    # show_data = models.DateTimeField(auto_now_add=True, verbose_name='上映时间')
    # vip_to_watch = models.IntegerField(verbose_name='会员电影', default=0)
    # is_free = models.IntegerField(verbose_name='是否免费', default=0)
    # price = models.IntegerField(verbose_name='价格', default=0)
    # area = models.CharField(max_length=15, verbose_name='地区')
    # lang = models.CharField(max_length=15, verbose_name='语言')
    like = models.IntegerField(verbose_name='点赞数')
    # dislike = models.IntegerField(verbose_name='点踩数')
    collections_num = models.IntegerField(verbose_name='收藏数')
    # be_bought = models.IntegerField(verbose_name='被购买次数', default=0)

    # 外键
    owner = models.ForeignKey("User", on_delete=models.SET_NULL, db_constraint=False, null=True,
                                       blank=True, verbose_name="视频拥有者")

    @property
    def owner_name(self):
        return self.owner.nice_name

    def __str__(self):
        return self.name
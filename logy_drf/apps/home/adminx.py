from django.contrib import admin

# Register your models here.
import xadmin
from . import models
# 注册
xadmin.site.register(models.Banner)
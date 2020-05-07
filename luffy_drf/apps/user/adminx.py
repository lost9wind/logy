from django.contrib import admin
from user import models
# Register your models here.
import xadmin


# 自定义xadmin主题
from xadmin import views
class GlobalSettings(object):
    """xadmin的全局配置"""
    site_title = "呆呆代练"  # 设置站点标题
    site_footer = "呆呆代练有限公司"  # 设置站点的页脚
    menu_style = "accordion"  # 设置菜单折叠
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(models.Movie)
xadmin.site.register(models.Word)
# xadmin.site.register(views.CommAdminView, GlobalSettings)
# xadmin.site.register(views.CommAdminView, GlobalSettings)
# xadmin.site.register(views.CommAdminView, GlobalSettings)
# xadmin.site.register(views.CommAdminView, GlobalSettings)
# xadmin.site.register(views.CommAdminView, GlobalSettings)



# xadmin默认会注册auth组件中的所有表
# from . import models
# xadmin.site.register(models.User)

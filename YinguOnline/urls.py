# -*- coding: UTF-8 -*-
"""YinguOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()
# from django.conf.urls import handler404, handler500, handler403
from django.contrib.auth.views import logout
from django.contrib.auth.views import login
# from django.contrib.auth import views as auth_views
from views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^index/$', index),  # 首页
    url(r'^$', index, name='index'),
    url(r'^accounts/login/$', login, {'template_name': 'login.htm'}),
    url(r'^accounts/logout/$', logout),
    url(r'^get_username/$', get_username),  # 获取当前登陆用户名
    url(r'^check_permission/$', check_permission),  # 检测用户权限
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

    # 人员
    # url(r'^people/', include('people.urls')),
    # 运营日报
    # url(r'^report/', include('report.urls')),
    # 监控
    # url(r'^monitor/', include('monitor.urls')),
    # 变更
    # url(r'^change/', include('change.urls')),
    # 数据库管理工具
    # url(r'^dtmt/', include('dtmt.urls')),
    # 定时任务
    url(r'^scheduled_tasks/', include('scheduled_tasks.urls')),
    # 业务查询
    # url(r'^business_query/', include('business_query.urls')),
    # 帮助(其它功能)
    # url(r'^help/', include('help.urls'))
]


# handler404 = page_not_found   #handler404
# handler403 = permission_denied   #handler403

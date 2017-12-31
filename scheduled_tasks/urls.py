# -*- coding: UTF-8 -*-
from django.conf.urls import url
from scheduled_tasks import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'YinguOnline.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

   url(r'^periodic_task/$', views.periodic_task),  # 周期任务
   url(r'^get_periodic_task_data/$', views.get_periodic_task_data),  # 周期任务 列表数据
   url(r'^add_periodic_task/$', views.add_periodic_task),  # 新增 周期任务
   url(r'^get_task_template/$', views.get_task_template),  # 获取任务模板列表 get tasks list
   url(r'^get_crontab/$', views.get_crontab),  # 新增 周期任务时 获取 crontab  定时时间
   url(r'^add_crontab/$', views.add_crontab),  # 新增 crontab  定时时间
   url(r'^get_database/$', views.get_database),  # 获取 数据库信息
   url(r'^add_periodic_task_data/$', views.add_periodic_task_data),  # 提交  新增周期任务 数据
   url(r'^test_periodic_task_data/$', views.test_periodic_task_data),  # 测试  新增周期任务 数据
   url(r'^test_periodic_task_result/$', views.test_periodic_task_result),  # 获取 测试  新增周期任务 结果
   url(r'^mod_periodic_task/(?P<id>\d+)/$', views.mod_periodic_task),  # 修改周期任务 页面
   url(r'^get_mod_periodic_task_data/$', views.get_mod_periodic_task_data),  # 获取 需要修改的周期任务 数据
   url(r'^mod_periodic_task_data/$', views.mod_periodic_task_data),  # 修改周期任务 数据
   url(r'^test_periodic_task_mod/$', views.test_periodic_task_mod),  # 测试 修改周期任务 数据
   url(r'^delete_periodic_task/$', views.delete_periodic_task),  # 删除 周期任务
   url(r'^crontabs/$', views.crontabs),  # crontab 定时时间
   url(r'^crontabs_get_data/$', views.crontabs_get_data),  # 获取 crontab 定时时间
   url(r'^add_crontab_index/$', views.add_crontab_index),  # 新增 crontab 定时时间 页面
   url(r'^mod_crontabs_index/(?P<id>\d+)/$', views.mod_crontabs_index),  # 修改 crontab 定时时间 页面
   url(r'^get_mod_crontab_data/$', views.get_mod_crontab_data),  # 获取需要修改的 crontab 定时时间 数据
   url(r'^delete_crontab/$', views.delete_crontab),  # 删除 crontab 定时时间 数据
]



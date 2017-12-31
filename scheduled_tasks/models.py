# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class ScheduledTask(models.Model):
    """
    投资批量查询
    """
    class Meta:
        db_table = 'scheduledTask'
        permissions = (
            ("viewTask", u"查看定时任务"),
            ("editTask", u"修改定时任务")
        )


class DataBaseInfo(models.Model):
    """
    数据库信息
    """
    name = models.CharField(max_length=255, null=True, blank=True, unique=True, verbose_name=u'名称')
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'描述')
    host = models.CharField(max_length=255, null=True, blank=True, unique=True, verbose_name=u'主机')
    user = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'用户')
    passwd = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'密码')
    db = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'数据库实例')
    type = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'数据库类型')

    def __unicode__(self):
        return '%s - %s - %s' % (self.name, self.host, self.type)

    class Meta:
        db_table = 'databaseinfo'
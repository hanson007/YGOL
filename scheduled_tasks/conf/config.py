#!/usr/bin/python env
# -*- coding: UTF-8 -*-
import sys
import os
reload(sys)
sys.setdefaultencoding("utf-8")
from django.conf import settings as _settings

_parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_YinguOnline_dir = os.path.dirname(_parentdir)
sys.path.append(_parentdir)
sys.path.append(_YinguOnline_dir)

_log_dir = _YinguOnline_dir + '/log/'
img_dir = _settings.STATICFILES_DIRS[0] + '/img/'
res_dir = u'/home/huangxiaoxue/mail_file/'
# res_dir = u'/data/'
unencrypted_res_dir = u'/tmp/'

# 日志文件
_logfilename = u'script_invest.log'
logfile = u'%s%s' % (_log_dir, _logfilename)

# 第三方 SMTP 服务
mail_host = "smtp.123.123.com"  # 设置服务器
mail_user = "huangxiaoxue"  # 用户名
mail_pass = "huangxiaoxue"  # 口令
# 发送人
sender = '229396865@qq.com'
sender_zh_name = u'LOL信息科技服务台'


# 数据库
databases = {
    'business1': {
        'name': u'业务1',
        'host': '1.1.1.1',
        'user': 'test',
        'passwd': 'test',
        'db': 'test'
    },
    'business2': {
        'name': u'业务2',
        'host': '1.1.1.2',
        'user': 'huangxiaoxue',
        'passwd': 'huangxiaoxue',
        'db': 'test'
    },
    'business3': {
        'name': u'业务3',
        'host': '1.1.1.3',
        'user': 'test',
        'passwd': 'test#',
        'db': 'test'
    }
}

# redis
host2 = '127.0.0.1'
port2 = 6379
db2 = 0

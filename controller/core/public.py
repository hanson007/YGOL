# -*- coding: UTF-8 -*-
import datetime


class Currency(object):
    #  通用帮助
    def __init__(self, request):
        self.request = request

    def rq_get(self, key):
        return self.request.GET.get(key, '').strip()

    def rq_post(self, key):
        return self.request.POST.get(key, '').strip()


class Datetime_help(object):
    # 日期时间帮助
    def __init__(self):
        self.now_time = datetime.datetime.now()

    def strptime(self, value, format):
        return datetime.datetime.strptime(value, format)

    @property
    def nowtimestrf1(self):
        return self.now_time.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def nowtimestrf2(self):
        return self.now_time.strftime('%Y年%m月%d日 %H点%M分%S秒')

    @property
    def nowtimestrf3(self):
        return self.now_time.strftime('%Y%m%d%H%M%S')

    @property
    def nowtimestrf4(self):
        return self.now_time.strftime('%Y%m%d')

    @property
    def nowtimestrf5(self):
        return self.now_time.strftime('%Y-%m-%d')

    @property
    def nowtimestrf6(self):
        return self.now_time.strftime(u'%Y年%m月%d日')

    @property
    def yesterday(self):
        yd = self.now_time - datetime.timedelta(days=1)
        return yd

    @property
    def yesterdaystrf4(self):
        return self.yesterday.strftime('%Y%m%d')

    @property
    def yesterdaystrf5(self):
        return self.yesterday.strftime('%Y-%m-%d')

    @property
    def yesterdaystrf6(self):
        return self.yesterday.strftime(u'%Y年%m月%d日')
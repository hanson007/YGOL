# -*- coding: UTF-8 -*-
##################################################
# Function:        自定义标签、过滤器
# Author:               黄小雪
# Date:				   2016年11月4日
# Company:         东方银谷
# Version:         1.2
##################################################
from django import template

register = template.Library()

@register.filter
def format_bool(value,args):
    data = args.split(',')
    return data[0] if value else data[1]


@register.filter
def request_type(key):
    types = {
        'CONFIRM_WITHHOLD':u'确认快捷充值',
        'CONFIRM_BIND_CARD':u'确认绑卡',
        'GATEWAY_WITHHOLD':u'确认网关充值',
        'PAYMENT_REQUEST':u'确认提现'
    }
    return types[key]

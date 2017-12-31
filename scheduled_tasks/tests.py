# -*- coding: UTF-8 -*-
# from django.test import TestCase
# from djcelery.schedulers import DatabaseScheduler
# Create your tests here.

# -*- coding: utf8 -*-
# from datetime import timedelta
# from celery import Celery
# app = Celery('hello', broker='redis://localhost:6379')
# app.conf.CELERYBEAT_SCHEDULE = {
#     "add-every-30-seconds": {
#         "task": "celery_app.hello",
#         "schedule": timedelta(seconds=30)
#     }
# }
# app.conf.CELERY_ROUTES = {
#     "celery_app.hello": {
#         "queue": "test"
#     }
# }
# app.conf.CELERY_TIMEZONE = "Asia/Shanghai"
# @app.task
# def hello():
#     return 'hello world'

def fun(**kwargs):
    print kwargs,kwargs.pop('a'),kwargs


para = {'a':1, 'b':2}

fun(**para)
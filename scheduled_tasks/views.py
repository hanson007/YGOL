# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response,render
from django.template import RequestContext
from django.http import HttpResponse
from djcelery.models import PeriodicTask, CrontabSchedule
from djcelery.schedulers import ModelEntry, DatabaseScheduler
from djcelery import loaders
from functools import wraps
from controller.core.public import Currency
from celery import registry
from celery import schedules
from mail_task import (test_mail)
from anyjson import loads, dumps
from django.db.models import Q
import redis
from conf.config import *
import datetime
import logging
import sys
import json
reload(sys)
sys.setdefaultencoding("utf-8")

# Create your views here.

logger = logging.getLogger('scheduled_tasks')
PAGE_SIZE = 10  # 每页显示条数
current_page_total = 10  # 分页下标


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def periodic_task(request):
    # 周期任务
    return render(request, 'scheduled_tasks/periodic_task.html', locals())


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def get_periodic_task_data(request):
    response = HttpResponse()
    rows = PeriodicTask.objects.values()
    nrows = [val_to(r) for r in rows]
    response.write(json.dumps(nrows))
    return response


def val_to(dt):
    new_dt = {}
    mail_tasks = ['mail_excel', 'mail_html']
    for k, v in dt.items():
        if isinstance(v, datetime.datetime):
            v = v.strftime("%Y-%m-%d %H:%M:%S")
        new_dt[k] = v
        if isinstance(v, bool):
            v = u'是' if v else u'否'
        new_dt[k] = v

    if dt['task'] in mail_tasks:
        jargs = dt['args']
        kwargs = json.loads(dt['kwargs'])
        is_encrypt = kwargs.pop('is_encrypt', False)
        receivers = kwargs['receivers']
        receivers_stf = '\n'.join([r.split('@')[0] for r in receivers])
        args = json.loads(jargs)
        subject = args[0]
        para_dtbs = [d['database'] for d in args[2]]
        para_dtbs_info = [u'%s %s' % (databases[p]['name'], databases[p]['host']) for p in para_dtbs]
        new_dt['is_encrypt'] = u'是' if is_encrypt else u'否'
        new_dt['subject'] = subject
        new_dt['databases'] = '\n'.join(set(para_dtbs_info))
        new_dt['receivers'] = receivers_stf

    crontab_id = dt['crontab_id']
    cron_stf = CrontabSchedule.objects.get(pk=crontab_id).__str__()
    new_dt['crontab'] = cron_stf
    return new_dt


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def add_periodic_task(request):
    # 新增 周期任务
    return render_to_response('scheduled_tasks/add_periodic_task.html', locals(), context_instance=RequestContext(request))


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def get_task_template(request):
    irrelevant_tasks = ['YinguOnline.celery.debug_task',
                        'backup_ygolp',
                        'celery.backend_cleanup',
                        'celery.chain',
                        'celery.chord',
                        'celery.chord_unlock',
                        'celery.chunks',
                        'celery.group',
                        'celery.map',
                        'celery.starmap',
                        'runing_invest_script']

    loaders.autodiscover()
    response = HttpResponse()
    tasks = list(sorted(registry.tasks.regular().keys()))
    for t in irrelevant_tasks:
        tasks.remove(t)
    response.write(json.dumps(tasks))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def get_crontab(request):
    # 获取 crontab 定时时间
    response = HttpResponse()
    data = CrontabSchedule.objects.values()
    response.write(json.dumps(list(data)))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def add_crontab(request):
    # 新增 crontab 定时时间
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    jdata = rq_post('data')
    data = json.loads(jdata)
    ndata = dict([(k, v.replace(' ', '')) for k, v in data.items()])  # Remove all spaces
    crobj = schedules.crontab(**ndata)
    to_model_schedule = ModelEntry.to_model_schedule
    model_schedule, model_field = to_model_schedule(crobj)
    response.write(json.dumps(ndata))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def get_database(request):
    # 获取 crontab 定时时间
    response = HttpResponse()
    response.write(json.dumps(databases))
    return response


def verification(check_class):
    """
    装饰器用于检测用户提交的信息是否合法.
    check_class 检测类
    Decorator for views that checks that the user submitted information,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            response = HttpResponse()
            ccl = check_class(request)
            check_status, error_msg = ccl.total_check()
            if check_status:
                response.write(json.dumps({'status': check_status, 'msg': error_msg}))
                return response

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


class Check_Periodic_Task(object):
    """
    检测新增周期任务提交的信息
    error_msg 存放所有错误消息
    check_status 错误状态 1 错误，0 正常，主要用于前端的JavaScript进行判断
    total_check 启动所有检测，返回检测状态和错误消息
    """
    def __init__(self, request):
        cur = Currency(request)
        rq_post = getattr(cur, 'rq_post')
        jdata = rq_post('data')
        data = json.loads(jdata)
        self.data = data
        self.error_msg = []
        self.task_name = data.get('task_name', '')
        self.task_template = data.get('task_template', '')
        self.is_enable = data.get('is_enable', '')
        self.is_encrypt = data.get('is_encrypt', '')
        self.mail_header = data.get('mail_header', '')
        self.receivers = data.get('receivers', [])
        self.cc = data.get('cc', [])
        self.crontab = data.get('crontab', '')
        self.sql_list = data.get('sql_list', '')

    def check_task_name(self):
        # 检测任务名称
        if not self.task_name:
            self.error_msg.append(u'任务名称不能为空')
        else:
            is_have = PeriodicTask.objects.filter(name=self.task_name).exists()
            if is_have:
                self.error_msg.append(u'任务名称已存在')

    def check_task_template(self):
        # 检测任务模板
        loaders.autodiscover()
        tasks = list(sorted(registry.tasks.regular().keys()))

        if self.task_template:
            if self.task_template not in tasks:
                self.error_msg.append(u'任务模板不存在')
        else:
            self.error_msg.append(u'任务模板不能为空')

    def check_is_enable(self):
        # 检测“是否启用”
        if not isinstance(self.is_enable, bool):
            self.error_msg.append(u'"是否启用" 值错误')

    def check_is_encrypt(self):
        # 检测“是否加密”
        if not isinstance(self.is_encrypt, bool):
            self.error_msg.append(u'"是否加密" 值错误')

    def check_mail_header(self):
        if not 0 < len(self.mail_header) < 30:
            self.error_msg.append(u'邮件标题不能为空或者超过30个字符')

    def check_receivers_cc(self):
        if not self.receivers and not self.cc:
            self.error_msg.append(u'收件人和抄送人不能全部为空')

    def check_crontab(self):
        crons = CrontabSchedule.objects.values('id')
        try:
            if long(self.crontab) not in [c['id'] for c in crons]:
                self.error_msg.append(u'执行时间错误')
        except Exception, e:
            self.error_msg.append(u'执行时间错误')

    def check_sql_list(self):
        if not self.sql_list:
            self.error_msg.append(u'SQL不能为空，至少包含一个SQL语句')
        else:
            for dt in self.sql_list:
                status = False
                if not dt['database']:
                    status = True
                    self.error_msg.append(u'%s SQL执行数据库不能为空' % (dt['sql_name']) )
                if not dt['sql']:
                    status = True
                    self.error_msg.append(u'%s SQL语句不能为空' % (dt['sql_name']))
                if not dt['sql_name']:
                    status = True
                    self.error_msg.append(u'SQL名称不能为空')
                if status:
                    break

    def total_check(self):
        self.check_task_name()
        self.check_task_template()
        self.check_is_enable()
        self.check_is_encrypt()
        self.check_mail_header()
        self.check_receivers_cc()
        self.check_crontab()
        self.check_sql_list()
        status = 1 if self.error_msg else 0

        return status, self.error_msg


class Check_Mod_Periodic_Task(Check_Periodic_Task):
    """
    检测修改周期任务提交的信息
    """
    def __init__(self, request):
        super(Check_Mod_Periodic_Task, self).__init__(request)
        self.task_id = self.data.get('_id', '')

    def check_task_name(self):
        # 检测任务名称
        if not self.task_name:
            self.error_msg.append(u'任务名称不能为空')
        else:
            Q_like = ~Q(id=int(self.task_id)) & Q(name=self.task_name)
            is_have = PeriodicTask.objects.filter(Q_like).exists()
            if is_have:
                self.error_msg.append(u'任务名称已存在')

    def check_task_id(self):
        # 检测任务ID
        if not self.task_id:
            self.error_msg.append(u'任务ID不能为空')
        else:
            is_have = PeriodicTask.objects.filter(pk=int(self.task_id)).exists()
            if not is_have:
                self.error_msg.append(u'任务ID不存在')

    def total_check(self):
        self.check_task_name()
        self.check_task_template()
        self.check_is_enable()
        self.check_is_encrypt()
        self.check_mail_header()
        self.check_receivers_cc()
        self.check_crontab()
        self.check_sql_list()
        self.check_task_id()
        status = 1 if self.error_msg else 0

        return status, self.error_msg


@login_required
@verification(Check_Periodic_Task)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def add_periodic_task_data(request):
    # 提交新增周期任务数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    jdata = rq_post('data')
    data = json.loads(jdata)

    cc = data['cc']
    crontab = data['crontab']
    is_enable = data['is_enable']
    is_encrypt = data['is_encrypt']
    # is_sensitive = data['is_sensitive']
    mail_header = data['mail_header']
    receivers = data['receivers']
    sql_list = data['sql_list']
    task_name = data['task_name']
    task_template = data['task_template']

    mailpara = {
        'mail_host': mail_host,
        'mail_user': mail_user,
        'mail_pass': mail_pass,
        'sender': sender,
        'sender_zh_name': sender_zh_name,
        'receivers': receivers,
        'cc': cc,
        'is_encrypt': is_encrypt,
    }

    schedule = CrontabSchedule.objects.get(pk=crontab).schedule
    create_or_update_task = DatabaseScheduler.create_or_update_task
    schedule_dict = {
        'schedule': schedule,
        'args': [mail_header, task_name, sql_list],
        'kwargs': mailpara,
        'task': task_template,
        'enabled': is_enable
    }
    create_or_update_task(task_name, **schedule_dict)
    # mail_excel(mail_header, task_name, sql_list, **mailpara)
    response.write(json.dumps({'status': 0, 'msg': ['操作成功']}))
    return response


@login_required
@verification(Check_Periodic_Task)
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def test_periodic_task_data(request):
    # 测试  新增周期任务 数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    jdata = rq_post('data')
    data = json.loads(jdata)
    test_mail(**data)
    response.write(json.dumps({'status': 0, 'msg': ['操作成功']}))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def test_periodic_task_result(request):
    # 获取 测试  新增周期任务 结果
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    _random = rq_post('_random')
    _r = redis.Redis(host=host2, port=port2, db=db2)

    msg = [_r.rpop(_random) for i in xrange(_r.llen(_random))]
    response.write(json.dumps({'msg': msg}))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def mod_periodic_task(request, id):
    # 修改 周期任务
    return render_to_response('scheduled_tasks/mod_periodic_task.html', locals(), context_instance=RequestContext(request))


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def get_mod_periodic_task_data(request):
    # 获取修改的周期任务数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    _id = rq_post('_id')
    obj = PeriodicTask.objects.get(pk=int(_id))
    data = {
        'name': obj.name,
        'task_template': obj.task,
        'crontab': obj.crontab.id,
        'args': obj.args,
        'kwargs': obj.kwargs,
        'enabled': obj.enabled,
    }
    response.write(json.dumps(data))
    return response


@login_required
@verification(Check_Mod_Periodic_Task)
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def mod_periodic_task_data(request):
    # 修改周期任务数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    jdata = rq_post('data')
    data = json.loads(jdata)

    _id = data['_id']
    cc = data['cc']
    crontab = data['crontab']
    is_enable = data['is_enable']
    is_encrypt = data['is_encrypt']
    # is_sensitive = data['is_sensitive']
    mail_header = data['mail_header']
    receivers = data['receivers']
    sql_list = data['sql_list']
    task_name = data['task_name']
    task_template = data['task_template']

    mailpara = {
        'mail_host': mail_host,
        'mail_user': mail_user,
        'mail_pass': mail_pass,
        'sender': sender,
        'sender_zh_name': sender_zh_name,
        'receivers': receivers,
        'cc': cc,
        'is_encrypt': is_encrypt,
    }
    schedule = CrontabSchedule.objects.get(pk=crontab)

    schedule_dict = {
        'crontab': schedule,
        'args': dumps([mail_header, task_name, sql_list]),
        'kwargs': dumps(mailpara),
        'task': task_template,
        'enabled': is_enable,
        'name': task_name
    }
    obj, _ = PeriodicTask._default_manager.update_or_create(
        id=int(_id), defaults=schedule_dict,
    )
    # mail_excel(mail_header, task_name, sql_list, **mailpara)
    response.write(json.dumps({'status': 0, 'msg': ['操作成功']}))
    return response


@login_required
@verification(Check_Mod_Periodic_Task)
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def test_periodic_task_mod(request):
    # 测试  修改周期任务 数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    jdata = rq_post('data')
    data = json.loads(jdata)
    test_mail(**data)
    response.write(json.dumps({'status': 0, 'msg': ['操作成功']}))
    return response


@login_required
@verification(Check_Mod_Periodic_Task)
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def delete_periodic_task(request):
    # 测试  修改周期任务 数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    jdata = rq_post('data')
    data = json.loads(jdata)
    _id = data.get('_id', '')
    PeriodicTask.objects.get(pk=int(_id)).delete()
    response.write(json.dumps({'status': 0, 'msg': ['操作成功']}))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def crontabs(request):
    # 周期任务的crontab 定时时间
    return render_to_response('scheduled_tasks/crontabs.html', locals(), context_instance=RequestContext(request))


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def crontabs_get_data(request):
    # 获取 crontab 定时时间数据
    response = HttpResponse()
    crontabs_obj = CrontabSchedule.objects.all()
    crontabs_stf = [{'id': c.id, 'crontab': c.__str__()} for c in crontabs_obj]
    response.write(json.dumps(crontabs_stf))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def add_crontab_index(request):
    # 新增 周期任务的crontab 定时时间 页面
    return render_to_response('scheduled_tasks/add_crontabs.html', locals(), context_instance=RequestContext(request))


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def mod_crontabs_index(request, id):
    # 修改 周期任务的crontab 定时时间 页面
    return render_to_response('scheduled_tasks/mod_crontabs.html', locals(), context_instance=RequestContext(request))


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
def get_mod_crontab_data(request):
    # 获取 需要修改的 crontab 定时时间 数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    _id = rq_post('id')
    fields = ['minute', 'hour', 'day_of_week', 'day_of_month', 'month_of_year']
    crontabs_obj = CrontabSchedule.objects.get(pk=int(_id))
    crontabs_stf = [getattr(crontabs_obj, f) for f in fields]
    response.write(json.dumps(dict(zip(fields, crontabs_stf))))
    return response


@login_required
@permission_required('scheduled_tasks.viewTask', raise_exception=PermissionDenied)
@permission_required('scheduled_tasks.editTask', raise_exception=PermissionDenied)
def delete_crontab(request):
    # 删除 crontab 定时时间 数据
    response = HttpResponse()
    cur = Currency(request)
    rq_post = getattr(cur, 'rq_post')
    jdata = rq_post('data')
    data = json.loads(jdata)
    _id = data.get('id', '')
    CrontabSchedule.objects.get(pk=int(_id)).delete()
    response.write(json.dumps(''))
    return response
#!/usr/bin/python env
# -*- coding: UTF-8 -*-
# Description:                    
# Author:           黄小雪
# Date:             2017年07月12日
# Company:          东方银谷
from conf.config import *
from controller.public.mysql_helper import *
from controller.core.public import *
from controller.core.excel import *
from controller.core.mailtable import *
from controller.public.mailclass import *
from celery import shared_task

import redis
import logging
import re

logger = logging.getLogger('scheduled_tasks')


class Logger_Redis(object):
    """
    同时在文件里和redis记录日志
    redis 里记录日志用于实时反馈结果
    """

    def __init__(self, key, logger):
        self.logger = logger
        # 本地缓存数据库 redis
        self._r = redis.Redis(host=host2, port=port2, db=db2)
        self.key = key

    def info(self, msg):
        self.logger.info(msg)
        self._r.lpush(self.key, msg)

    def error(self, msg):
        self.logger.error(msg)
        self._r.lpush(self.key, msg)


class Database_Connection(object):
    # 数据库连接
    def __init__(self, logger):
        for dtbs, para in databases.items():
            dtc = Business(para['host'], para['user'],
                           para['passwd'], para['db'],
                           logger)
            setattr(self, dtbs, dtc)


class Data(Database_Connection):
    def __init__(self, logger):
        super(Data, self).__init__(logger)

    def _query_data(self, sql, dtbs):
        dtc = getattr(self, dtbs)
        data = dtc.getall_list(sql)
        rows = []
        if data:
            rows = [self._get_row(dt) for dt in data]

        return rows

    def get_rows(self, sql, dtbs):
        rows = self._query_data(sql, dtbs)
        dtc = getattr(self, dtbs)
        status = dtc.status
        rows.insert(0, dtc.row0)
        return rows, status

    def creat_excel(self, total_rows, resfile):
        # 创建工作簿
        opxl = Openpyxl(resfile)
        for title, rows in total_rows:
            opxl.add_sheet(title, rows)
        opxl.save()

    def creat_tables(self, allrows):
        # 创建工作簿
        mtable = MailTable()
        style = getattr(mtable, 'style')
        tables = [mtable.table(caption, rows) for caption, rows in allrows]
        tablestr = '<br>'.join(tables)
        # self.log.info(u'%s 执行完成' % subject)
        return tablestr, style

    def _get_row(self, dt):
        ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

        row = []
        for val in dt:
            if isinstance(val, long):
                val = str(val)
            if isinstance(val, str) and next(ILLEGAL_CHARACTERS_RE.finditer(val), None):
                val = ord(val)
            row.append(val)

        return row


class Send_Mail(object):
    # 发送邮件
    def __init__(self, subject, date_time, resfile, logger, **mailpara):
        self.subject = subject
        self.date_time = date_time
        self.resfile = resfile
        self.hmail = MailHelper(logger=logger, **mailpara)

    @property
    def text(self):
        _text = """
        <p>各位领导 你好：</p>
        <p style="margin-left:100px;">%s%s数据，请知晓，谢谢。</p>
        <hr />
        <p><font color="#00dddd">运维服务台</font></p>
        <p><font color="#00dddd">系统运维中心</font></p>
        <p><font color="#00dddd">运维中心7*24值班电话：1111111111</font></p>
        <p><font color="#00dddd">扫一扫二维码，加我微信</font></p>
        <p><img src="cid:image1"/></p>
        """ % (self.subject, self.date_time)
        return _text

    @property
    def date_subject(self):
        return u'%s_%s' % (self.subject, self.date_time)

    def send(self):
        # 执行发送
        self.hmail.add_content(self.text, self.date_subject)
        self.hmail.add_attch(self.resfile)
        self.hmail.insert_img(img_dir + 'catch.jpg')
        self.hmail.send_htm()


@shared_task(name='mail_excel')
def mail_excel(subject, task_name, sql_list, **kwargs):
    data = Data(logger)
    _dt = Datetime_help()
    is_encrypt = kwargs.pop('is_encrypt')
    resfilename = u'%s%s.xlsx' % (task_name, _dt.nowtimestrf4)
    resfile = u'%s%s' % (res_dir if is_encrypt else unencrypted_res_dir, resfilename)

    total_rows = []
    for dt in sql_list:
        rows, status = data.get_rows(dt['sql'], dt['database'])
        if status:
            wk = (dt['sql_name'], rows)
            total_rows.append(wk)
            logger.info(u'%s SQL 执行完成' % dt['sql_name'])
    data.creat_excel(total_rows, resfile)
    logger.info(u'%s 执行完成' % resfilename)
    smail = Send_Mail(subject, _dt.nowtimestrf6, resfile, logger, **kwargs)
    smail.send()


def test_mail_excel(**data):
    # 测试 邮件excel
    cc = data['cc']
    mail_header = data['mail_header']
    receivers = data['receivers']
    sql_list = data['sql_list']
    task_name = data['task_name']
    _random = data['_random']
    is_encrypt = data.pop('is_encrypt')

    mailpara = {
        'mail_host': mail_host,
        'mail_user': mail_user,
        'mail_pass': mail_pass,
        'sender': sender,
        'sender_zh_name': sender_zh_name,
        'receivers': receivers,
        'cc': cc,
    }

    logger_redis = Logger_Redis(_random, logger)
    data = Data(logger_redis)
    _dt = Datetime_help()
    resfilename = u'%s%s.xlsx' % (task_name, _dt.nowtimestrf4)
    resfile = u'%s%s' % (res_dir if is_encrypt else unencrypted_res_dir, resfilename)
    total_rows = []
    for dt in sql_list:
        rows, status = data.get_rows(dt['sql'], dt['database'])
        if not status:
            return None
        wk = (dt['sql_name'], rows)
        total_rows.append(wk)
        logger_redis.info(u'%s SQL 执行完成' % dt['sql_name'])
    data.creat_excel(total_rows, resfile)
    logger_redis.info(u'%s 执行完成' % resfilename)
    smail = Send_Mail(mail_header, _dt.nowtimestrf6, resfile, logger_redis, **mailpara)
    smail.send()


@shared_task(name='mail_html')
def mail_html(subject, task_name, sql_list, **kwargs):
    data = Data(logger)
    _dt = Datetime_help()
    kwargs.pop('is_encrypt')
    mailpara = kwargs

    total_rows = []
    for dt in sql_list:
        rows, status = data.get_rows(dt['sql'], dt['database'])
        if status:
            wk = (dt['sql_name'], rows)
            total_rows.append(wk)
            logger.info(u'%s SQL 执行完成' % dt['sql_name'])
    tablestr, style = data.creat_tables(total_rows)
    logger.info(u'%s 执行完成' % subject)
    smail = Send_Mail_Html(subject, _dt.nowtimestrf6, tablestr, style, logger, **mailpara)
    smail.send()


class Send_Mail_Html(object):
    # 发送邮件
    def __init__(self, subject, date_time, tablestr, style, logger, **mailpara):
        self.subject = subject
        self.date_time = date_time
        self.style = style
        self.tablestr = tablestr
        self.hmail = MailHelper(logger=logger, **mailpara)

    @property
    def text(self):
        _text = """
            %s
        <p>各位领导 你好：</p>
        <p style="margin-left:100px;">%s%s数据，请知晓，谢谢。</p>
            %s
        <hr />
        <p><font color="#00dddd">运维服务台</font></p>
        <p><font color="#00dddd">系统运维中心</font></p>
        <p><font color="#00dddd">运维中心7*24值班电话：11111111</font></p>
        <p><font color="#00dddd">扫一扫二维码，加我微信</font></p>
        <p><img src="cid:123"/></p>
        """ % (self.style, self.date_time, self.subject, self.tablestr)
        return _text

    @property
    def date_subject(self):
        return u'%s_%s' % (self.subject, self.date_time)

    def send(self):
        # 执行发送
        self.hmail.add_content(self.text, self.date_subject)
        self.hmail.insert_img(img_dir + 'catch.jpg')
        self.hmail.send_htm()


def test_mail_html(**data):
    # 测试 邮件html 表格
    cc = data['cc']
    mail_header = data['mail_header']
    receivers = data['receivers']
    sql_list = data['sql_list']
    task_name = data['task_name']
    _random = data['_random']

    mailpara = {
        'mail_host': mail_host,
        'mail_user': mail_user,
        'mail_pass': mail_pass,
        'sender': sender,
        'sender_zh_name': sender_zh_name,
        'receivers': receivers,
        'cc': cc,
    }

    logger_redis = Logger_Redis(_random, logger)
    data = Data(logger_redis)
    _dt = Datetime_help()

    total_rows = []
    for dt in sql_list:
        rows, status = data.get_rows(dt['sql'], dt['database'])
        if not status:
            return None
        wk = (dt['sql_name'], rows)
        total_rows.append(wk)
        logger_redis.info(u'%s SQL 执行完成' % dt['sql_name'])
    tablestr, style = data.creat_tables(total_rows)
    logger_redis.info(u'%s 执行完成' % mail_header)
    smail = Send_Mail_Html(mail_header, _dt.nowtimestrf6, tablestr, style, logger_redis, **mailpara)
    smail.send()


def test_mail(**data):
    # 测试邮件
    all_fun = {"mail_excel": test_mail_excel, "mail_html": test_mail_html}
    fun = all_fun.get(data['task_template'])
    fun(**data)

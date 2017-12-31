#! /usr/bin/env python
# -*-coding:utf-8-*-
##################################################
# Function:        银谷在线注册统计及出借统计脚本
# Usage:                python start.py
# Author:               黄小雪
# Date:                 2016年7月19日
# Company:
# Version:        1.2
##################################################
import MySQLdb


class MysqlHelper(object):
    """
    数据访问层
    status：查询状态,True 查询正常，False 查询失败,默认为True
    """
    def __init__(self, host, user, passwd, db, logger):
        self.__host = host
        self.__user = user
        self.__passwd = passwd
        self.__db = db
        self._logger = logger
        self.row0 = None
        self.rowcount = None
        self.error_msg = ''
        self.status = True

    def __conn(self):
        try:
            conn = MySQLdb.connect(host=self.__host, user=self.__user,
                                   passwd=self.__passwd, db=self.__db,
                                   init_command="set names utf8",
                                   charset='utf8')
        except Exception, e:
            self.error_msg = '%s' % e
            self._logger.error(e)
            self.status = False
            conn = None
        return conn

    def getall(self, sql, paramters=None):
        conn = self.__conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)  # 返回字典
            cur.execute(sql, paramters)
            data = cur.fetchall()
            self.rowcount = cur.rowcount
            self.row0 = [d[0] for d in cur.description]
        except Exception, e:
            self.error_msg = '%s' % e
            self._logger.error(e)
            data = None
        finally:
            cur.close()
            conn.commit()
            conn.close()
        return data

    def getallmany(self, sql, paramters=None):
        conn = self.__conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)  # 返回字典
            cur.executemany(sql, paramters)
            data = cur.fetchall()
        except Exception, e:
            self._logger.error(e)
            data = None
        finally:
            cur.close()
            conn.commit()
            conn.close()
        return data

    def getsingle(self, sql, paramters=None):
        conn = self.__conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)  # 返回字典
            cur.execute(sql, paramters)
            data = cur.fetchone()
        except Exception, e:
            # print e
            self._logger.error(e)
            data = None
        finally:
            cur.close()
            conn.commit()
            conn.close()
        return data

    def insertmany(self, sql, paramters=None):
        conn = self.__conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)  # 返回字典
            cur.executemany(sql, paramters)
        except Exception, e:
            self._logger.error(e)
        finally:
            cur.close()
            conn.commit()
            conn.close()
        return None

    def getall_list(self, sql, paramters=None):
        # 返回列表形式结果
        conn = self.__conn()
        if not conn:
            return None
        try:
            cur = conn.cursor()  # 返回列表
            cur.execute(sql, paramters)
            data = cur.fetchall()
            self.rowcount = cur.rowcount
            self.row0 = [d[0] for d in cur.description]
        except Exception, e:
            self.error_msg = '%s' % e
            self._logger.error(e)
            self.status = False
            data = None
        finally:
            cur.close()
            conn.commit()
            conn.close()
        return data

    def getall_list_sqls(self, sqls, paramters=None):
        """
            执行多个sql语句，返回列表形式结果
            sqls = [sql1, sql2, ... ...]
        """

        conn = self.__conn()
        if not conn:
            return None
        try:
            cur = conn.cursor()  # 返回列表
            for sql in sqls:
                cur.execute(sql, paramters)
            data = cur.fetchall()
            self.rowcount = cur.rowcount
            self.row0 = [d[0] for d in cur.description]
        except Exception, e:
            self._logger.error(e)
            data = None
        finally:
            cur.close()
            conn.commit()
            conn.close()
        return data

    def delete(self, sql, paramters=None):
        conn = self.__conn()
        if not conn:
            return None
        try:
            cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)  # 返回字典
            cur.execute(sql, paramters)
        except Exception, e:
            self.error_msg = '%s' % e
            self._logger.error(e)
        finally:
            cur.close()
            conn.commit()
            conn.close()
        return None


class Business(MysqlHelper):
    # 业务处理层
    def __init__(self, host, user, passwd, db, logger):
        super(Business, self).__init__(host, user, passwd, db, logger)

    def insert(self, sql, para=None):
        return self.getsingle(sql, para)

    def search(self, sql, para=None):
        return self.getsingle(sql, para)

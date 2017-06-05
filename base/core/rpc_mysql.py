# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：rpc_mysql.py
# 日期：2017/3/13-16:15
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
import sys
sys.path.append("../PYReactor/lib")
sys.path.append("../PYReactor/core")
from mysql_client import *
from pb_msg import *
import opmysql_pb2
from json_parse import *
from rpc_service import *
from log import *
from rpc_comm import *

class RpcMySql():

    m_Conn = None

    def __init__(self):
        mySQL = MySQLService()

    @classmethod
    def InitMySql(cls, host, port, user, passwd, dbname):
        cls.m_Conn = CMySql()
        ret = cls.m_Conn.Connect(host, port, user, passwd, dbname)
        log_debug("ret:%d", ret)

    @classmethod
    def OpMySql(cls, request, ctrl):
        log_debug("request type:%d", request.pb_msg.type)
        if request.pb_msg.type == const.MYSQL_OP_INSERT:
            return cls.MySqlInsert(request, ctrl)
        elif request.pb_msg.type == const.MYSQL_OP_DELETE:
            return cls.MySqlDelete(request, ctrl)
        elif request.pb_msg.type == const.MYSQL_OP_UPDATE:
            return  cls.MySqlUpdate(request ,ctrl)
        elif request.pb_msg.type == const.MYSQL_OP_SELECT:
            return cls.MySqlSelect(request, ctrl)

    @classmethod
    def MySqlInsert(cls, request,ctrl):
        sql = request.pb_msg.sql
        response = PbMessage(opmysql_pb2.MySQLResponse())
        ctrl.SetSuccess()
        if cls.m_Conn is not None:
            ret = cls.m_Conn.Insert(sql)
            if ret < 0:
                response.pb_msg.code = -1
                response.pb_msg.msg = "Operate Failed!"
                log_debug("Operate Failed!")
                return response, ctrl
            else:
                response.pb_msg.code = ret
                response.pb_msg.msg = "Operate Success, Insert %d records!" % ret
                log_debug("Operate Success, Insert %d records!", ret)
                return response, ctrl
        else:
            response.pb_msg.code = -1
            response.pb_msg.msg = "MySQL Not Connect!"
            log_debug("MySQL Not Connect!")
            return response,ctrl

    @classmethod
    def MySqlDelete(cls,request,ctrl):
        sql = request.pb_msg.sql
        response = PbMessage(opmysql_pb2.MySQLResponse())
        ctrl.SetSuccess()
        if cls.m_Conn is not None:
            ret = cls.m_Conn.Delete(sql)
            if ret < 0:
                response.pb_msg.code = -1
                response.pb_msg.msg = "Operate Failed!"
                log_debug("Operate Failed!")
                return response,ctrl
            else:
                response.pb_msg.code = ret
                response.pb_msg.msg = "Operate Success, Delete %d records!" % ret
                log_debug("Operate Success, Delete %d records!", ret)
                return response,ctrl
        else:
            response.pb_msg.code = -1
            response.pb_msg.msg = "MySQL Not Connect!"
            log_debug("MySQL Not Connect!")
            return response, ctrl

    @classmethod
    def MySqlUpdate(cls, request,ctrl):
        sql = request.pb_msg.sql
        response = PbMessage(opmysql_pb2.MySQLResponse())
        ctrl.SetSuccess()
        if cls.m_Conn is not None:
            ret =cls.m_Conn.Update(sql)
            if ret < 0:
                response.pb_msg.code = -1
                response.pb_msg.msg = "Operate Failed!"
                log_debug("Operate Failed!")
                return response,ctrl
            else:
                response.pb_msg.code = ret
                response.pb_msg.msg = "Operate Success, Update %d records!" % ret
                log_debug("Operate Success, Update %d records!", ret)
                return response,ctrl
        else:
            response.pb_msg.code = -1
            response.pb_msg.msg = "MySQL Not Connect!"
            log_debug("MySQL Not Connect!")
            return response,ctrl

    @classmethod
    def MySqlSelect(cls, request,ctrl):
        sql = request.pb_msg.sql
        response = PbMessage(opmysql_pb2.MySQLResponse())
        ctrl.SetSuccess()
        log_debug("sql:%s",sql)
        if cls.m_Conn is not None:
            ret = cls.m_Conn.SelectAll(sql)
            if ret < 0:
                response.pb_msg.code = -1
                response.pb_msg.msg = "Operate Failed!"
                log_debug("Operate Failed!")
                return response,ctrl
            else:
                js = CJson()
                result = js.Write(ret)
                response.pb_msg.sqlret = result
                response.pb_msg.code = len(ret)
                response.pb_msg.msg = "Operate Success, Select %d records!" % len(ret)
                log_debug("Operate Success, Select %d records!, typ:%s", len(ret),type(ret))
                return response,ctrl
        else:
            response.pb_msg.code = -1
            response.pb_msg.msg = "MySQL Not Connect!"
            log_debug("MySQL Not Connect!")
            return response,ctrl


class MySQLService(RpcService):

    def __init__(self):
        self.name = "MySQLService"
        self.full_name = "MySQL.MySQLService"

        req_msg = opmysql_pb2.MySQLRequest()
        rsp_msg = opmysql_pb2.MySQLResponse()

        req = PbMessage(req_msg)
        rsp = PbMessage(rsp_msg)

        method = RpcMethod("MySQL", "MySQLService.MySQL", req, rsp, self)
        MethodManager.RegisterMethod(method)
        log_debug("register mysql service!")

    def __del__(self):
        pass

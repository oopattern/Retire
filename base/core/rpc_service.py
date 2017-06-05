# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：rpc_service.py
# 日期：2017/2/13-12:19
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
from log import *
class RpcMethod:
     def __init__(self, name, full_name, request, response, service):
         self.name = name
         self.full_name = full_name
         self.request_type = request
         self.response_type = response
         self.service = service

     def __del__(self):
         pass

     def new_request(self):
         log_debug("request_type:%s", type(self.request_type))
         return self.request_type.New()

     def new_response(self):
         return self.response_type.New()

class MethodManager:

    method_name_map = {}

    def __init__(self):
        pass

    def __del__(self):
        pass

    @classmethod
    def RegisterMethod(self, method):
        log_debug("name:%s", method.full_name)
        self.method_name_map[method.full_name] = method
        print self.method_name_map

    @classmethod
    def Method(self, method_full_name):
        log_debug("name:%s", method_full_name)
        log_debug("%s", self.method_name_map)
        return self.method_name_map[method_full_name]

class RpcService:
    service_name_map = {}

    def __init__(self):
        self.name = ""
        self.full_name = ""
        self.method_name_map = {}

    def __del__(self):
        pass

    def CallMethod(self, method, controller, rquest, reponse):
        pass;

class RpcCtrl:
    def __init__(self):
        self.m_errno = -1

    def __del__(self):
        pass

    def Reset(self):
        self.m_errno = -1

    def Failed(self):
        return (0 != self.m_errno)

    def Success(self):
        return (0 == self.m_errno)

    def GetRet(self):
        return self.m_errno

    def ErrorText(self):
        pass

    def SetSuccess(self):
        self.m_errno = 0

    @classmethod
    def SetFiled(self, ret):
        self.m_errno =  ret

class RpcChannel:

    def __init__(self):
        pass

    def __del__(self):
        pass

    def CallMethod(self, method, controller, request, response):
        pass



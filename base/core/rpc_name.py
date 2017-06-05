# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：rpc_name.py
# 日期：2017/3/1-15:06
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
from log import *

class RpcName:

    m_ServiceList = {}

    def __init__(self):
        pass

    def __del__(self):
        pass

    @classmethod
    def RigisterSelfInfo(self, svid, type):
        self.svid = svid
        self.type = type

    @classmethod
    def GetSelfSvid(self):
        return self.type, self.svid

    @classmethod
    def GetSvidByService(self, service_name):
        svr_type = 0
        svr_id = 0
        group = 0
        str = "%s_%d" % (service_name, group)
        log_debug("servicelist:%s", self.m_ServiceList)
        if self.m_ServiceList[str] is not None:
            svr_type = self.m_ServiceList[str]["srv_type"]
            svr_id = self.m_ServiceList[str]["svid"]
            log_debug("GetSvidByService svid = %d, svr_type = %d", svr_id, svr_type)
        return svr_type,svr_id

    @classmethod
    def GetSvidBySvid(self,service_name, svid):
        svr_type = 0
        svr_id = 0
        for k,v in self.m_ServiceList.items():
            if v["svid"] == svid:
                svr_type = v["svr_type"]
                svr_id = v["svr_id"]
                log_debug("GetSvidBySvid svid:%d, type:%d", v.svid, v.svr_type)
        return svr_type, svr_id

    @classmethod
    def GetSvidByMod(self, service_name, mod_key):
        svr_type = 0
        svr_id = 0

        return svr_type, svr_id

    @classmethod
    def GetSvidByGroup(self, service_name, group_id):
        svr_type = 0
        svr_id = 0
        for k,v in self.m_ServiceList.items():
            if v["srv_group"] == group_id:
                svr_type = v["srv_type"]
                svr_id = v["svid"]
                log_debug("GetSvidByGroup svid:%d, type:%d", v.svid, v.svr_type)
        return svr_type,svr_id

    @classmethod
    def ReloadServiceList(self, server_list):
        for v in server_list:
            str = "%s_%d" % (v.srv_name, v.srv_group)
            log_debug("str:%s, size:%d", str, len(server_list))
            self.m_ServiceList[str] = {"srv_name" : v.srv_name, "srv_group" : v.srv_group, "srv_type": v.srv_type, "svid" : v.svid, "srv_dispatch" : v.srv_dispatch, "add_time" : v.add_time }
            log_debug("service:%s", self.m_ServiceList[str])
            log_debug("ReloadServiceList srv_name:%s, svid = %d, dispatch_svid = %d， type:%d",v.srv_name,v.svid,v.srv_dispatch,v.srv_group)

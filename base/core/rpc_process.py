# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：rpc_process.py
# 日期：2017/2/14-9:35
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
import rpc_pb2
from log import *
from rpc_comm import *
from rpc_service import *
from baseserver import *
from tcpclient import *
from pb_msg import *
from rpc_name import *
from rpc_mysql import *
from adaptor import *
from pb_msg import *


class RpcProcess:

    def __init__(self):
        pass

    def __del__(self):
        pass

    @classmethod
    def RpcRpcPacket(cls, input, jd_head):
        head_buf = input.ReadBinary()
        rpc_head = PbMessage(rpc_pb2.RpcHead())
        if not rpc_head.Decode(head_buf):
            log_err("parse rpc head proto err!!!")
            return

        msg_type = rpc_head.pb_msg.msg_type
        if not msg_type:
            log_debug("rpc head no require [msg_type] feild!")
            return
        log_debug("type:%d", rpc_head.pb_msg.msg_type)
        if const.RPC_TYPE_REQUEST == rpc_head.pb_msg.msg_type:
            req_buf = input.ReadBinary()
            log_debug("req:%s", req_buf)
            return cls.RpcRequest(jd_head, rpc_head, req_buf)
        elif const.RPC_TYPE_RESPONSE == rpc_head.pb_msg.msg_type:
            rsp_buf = input.ReadBinary()
            return cls.RpcResponse(rpc_head, rsp_buf)
        else:
            log_debug("rpc head err msg type, type=%d", rpc_head.msg_type)

        return 0

    @classmethod
    def RpcRequest(cls, jd_head, rpc_head, req_buf):
        method = MethodManager.Method(rpc_head.pb_msg.method_name)
        log_debug("name:%s", rpc_head.pb_msg.method_name)
        request = method.new_request()
        response = method.new_response()

        if not request.Decode(req_buf):
            log_debug(
                "rpc method=[%s] request  proto parse err", rpc_head.method_name)
        ctrl = RpcCtrl()
        service = method.service
        log_debug("service:%s, name:%s, kk:%s", type(service), rpc_head.pb_msg.method_name, const.MYSQL_SERVICE)
        if rpc_head.pb_msg.method_name == "MySQLService.MySQL":
            res, controller = RpcMySql.OpMySql(request, ctrl)
        else:
            res, controller=service.CallMethod(method, ctrl, request, response)
        output=JDOutput()
        output.Begin()

        jd_head.pb_msg.dst_type=jd_head.pb_msg.src_type
        jd_head.pb_msg.dst_svid=jd_head.pb_msg.src_svid
        jd_head.src_type, jd_head.pb_msg.src_svid=RpcName.GetSelfSvid()
        jd_head_buf=jd_head.Encode()
        output.WriteBinary(jd_head_buf)

        ret=RpcCtrl().GetRet()
        rpc_head.pb_msg.msg_type=const.RPC_TYPE_RESPONSE
        rpc_head.pb_msg.result=controller.GetRet()
        head_str=rpc_head.Encode()
        output.WriteBinary(head_str)
        print controller.GetRet()
        if controller.GetRet() >= 0:
            resp_str=res.Encode()
            output.WriteBinary(resp_str)
        output.End()
        cls.SendPacket(output)

    @classmethod
    def RpcResponse(cls, rpc_head, rsp_buf):
        method=MethodManager.Method(rpc_head.pb_msg.method_name)
        log_debug("name:%s", rpc_head.pb_msg.method_name)
        request=method.new_request()
        response=method.new_response()

        if not response.Decode(rsp_buf):
            log_debug(
                "rpc method=[%s] response  proto parse err", rpc_head.method_name)

        log_debug("rsp:%s", response.pb_msg.result)
        ctrl=RpcCtrl()
        service=method.service
        log_debug("service:%s", type(service))
        service.CallMethod(method, ctrl, request, response)

    @classmethod
    def SendAndRecv(cls, head_msg, output, response, ctrl, timeout):
        cls.SendPacket(output)

    @classmethod
    def SendPacket(cls, output):
        log_debug("send")
        handler=Adaptor.GetDispacthcHandler()
        handler.SendPacket(output)

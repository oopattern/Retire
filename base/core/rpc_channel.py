# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：rpc_channel.py
# 日期：2017/2/13-11:24
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
import sys
sys.path.append("../proto")
from packet import *
from rpc_comm import *
import rpc_pb2
from rpc_service import *
from log import *
import jdhead_pb2
from pb_msg import *
from rpc_name import *
import rpc_process


class JdRpcChannel:

    def __init__(self):
        pass

    def CallMethod(self, method, contorller, request, response, dst_type, dst_svid):
        output = JDOutput()
        output.Begin()

        jd_head = PbMessage(jdhead_pb2.JDHead())
        jd_head.pb_msg.msg_type = const.RPC_TYPE_REQUEST
        jd_head.pb_msg.cmd = const.RPC_CMD
        jd_head.pb_msg.dst_type = dst_type
        jd_head.pb_msg.dst_svid = dst_svid
        jd_head.pb_msg.src_type, jd_head.pb_msg.src_svid = RpcName().GetSelfSvid()
        jd_head_buf = jd_head.Encode()
        output.WriteBinary(jd_head_buf)

        head_msg = PbMessage(rpc_pb2.RpcHead())

        head_msg.pb_msg.sequence = newseq()
        head_msg.pb_msg.msg_type = const.RPC_TYPE_REQUEST
        head_msg.pb_msg.method_name = method.full_name
        head_msg.pb_msg.flow_id = 0
        head_msg.pb_msg.result = 0

        head_str = head_msg.Encode()
        req = request.Encode()
        output.WriteBinary(head_str)
        output.WriteBinary(req)
        output.End()

        rpc_process.RpcProcess.SendAndRecv(
            head_msg, output, response, contorller, 3)

    def SendMessage(self, method, request, dst_type, dst_svid):
        outPkg = JDOutput()
        outPkg.Begin()

        jd_head = PbMessage(jdhead_pb2.JDHead())
        jd_head.pb_msg.msg_type = const.RPC_TYPE_REQUEST
        jd_head.pb_msg.cmd = const.RPC_CMD
        jd_head.pb_msg.dst_type = dst_type
        jd_head.pb_msg.dst_svid = dst_svid
        jd_head.pb_msg.src_type, jd_head.pb_msg.src_svid = RpcName.GetSelfSvid()

        jd_head_buf = jd_head.Encode()

        head_msg = PbMessage(rpc_pb2.RpcHead())
        head_msg.pb_msg.sequence = newseq()
        head_msg.pb_msg.msg_type = const.RPC_TYPE_REQUEST
        head_msg.pb_msg.method_name = method.full_name
        head_msg.pb_msg.flow_id = 0
        head_msg.pb_msg.result = 0

        head_str = head_msg.Encode()
        outPkg.WriteBinary(head_str)

        req_str = request.Encode()
        outPkg.WriteBinary(req_str)
        outPkg.End()

        ret = RpcProcess.SendPacket(outPkg)

def call_method(method, req, dst_type, dst_svid):
    request = method.new_request()
    response = method.new_response()

    if not request or not response or not req:
        log_err("method=[%s] create message failed ", method.full_name)
        return const.SRPC_ERR_PARA_ERROR

    # for orig_key, orig_value in req:
    request.pb_msg = req

    controller = RpcCtrl()
    rpc_channel = JdRpcChannel()

    rpc_channel.CallMethod(method, controller, request,
                           response, dst_type, dst_svid)

    if controller.Failed():
        return controller.GetRet()

    return 0, response

def CallMethod(method_full_name, req):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidByService(method.service.full_name)
    log_debug("dsttype:%s, dstsvid:%d", dst_type, dst_svid)
    return call_method(method, req, dst_type, dst_svid)


def CallMethodBySvid(method_full_name, req, svid):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidBySvid(method.service.full_name, svid)
    return call_method(method, req, dst_type, dst_svid)


def CallMethodByMod(method_full_name, req, mod_key):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidByMod(
        method.service.full_name, mod_key)
    return call_method(method, req, dst_type, dst_svid)


def CallMethodByGroup(method_full_name, req, group_id):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidByGroup(
        method.service.full_name, group_id)
    return call_method(method, req, dst_type, dst_svid)


def send_message(method, req, dst_type, dst_svid):
    request = method.new_request()

    if not request or not req:
        log_err("method=[%s] create message failed ", method.full_name)
        return const.SRPC_ERR_PARA_ERROR

    for orig_key, orig_value in req.items():
        request.pb_msg[orig_key] = orig_value

    rpc_channel = JdRpcChannel()
    return rpc_channel.SendMessage(method, request, dst_type, dst_svid)


def SendMessage(method_full_name, req):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidByService(method.service.full_name)
    send_message(method, req, dst_type, dst_svid)
    return 0


def SendMessageBySvid(method_full_name, req, svid):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidBySvid(method.service.full_name, svid)
    send_message(method, req, dst_type, dst_svid)
    return 0


def SendMessageByMod(method_full_name, req, mod_key):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidByMod(
        method.service.full_name, mod_key)
    send_message(method, req, dst_type, dst_svid)
    return 0


def SendMessageByGroup(method_full_name, req, group_id):
    method = MethodManager.Method(method_full_name)
    if not method:
        log_err("method=[%s] not find in client ", method_full_name)
        return const.SRPC_ERR_INVALID_METHOD_NAME

    dst_type, dst_svid = RpcName.GetSvidByGroup(
        method.service.full_name, group_id)
    send_message(method, req, dst_type, dst_svid)
    return 0


def PbHeadConstructor(output, cmd, msg_type):
    jd_head = PbMessage(jdhead_pb2.JDHead())
    jd_head.pb_msg.msg_type = msg_type
    jd_head.pb_msg.cmd = cmd
    jd_head.pb_msg.dst_type = 0
    jd_head.pb_msg.dst_svid = 0
    jd_head.pb_msg.src_type, jd_head.pb_msg.src_svid = RpcName.GetSelfSvid()
    jd_head_buf = jd_head.Encode()
    output.WriteBinary(jd_head_buf)

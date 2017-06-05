# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：rpc_game.py
# 日期：2017/2/14-9:40
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
import sys
sys.path.append("../proto")
from rpc_process import *
from baseserver import *
from rpc_process import *
from tcpclient import *
from pb_msg import *
import jdhead_pb2
from rpc_comm import *

class RpcServer(CBaseServer):

    def __init__(self):
        self.curr_slot = None
        pass

    def __del__(self):
        pass

    def ProcJdPacket(self, slot, input, jd_head):
        return 0

    def ProcessJdPacket(self, slot, input):
        self.curr_slot = slot

        jd_head_buf = input.ReadBinary()
        jd_head = PbMessage(jdhead_pb2.JDHead())

        if not jd_head.Decode(jd_head_buf):
            log_debug("parse jd head proto err!!!")
            return

        log_debug("msg_type=%d, ,cmd=0x%x", jd_head.pb_msg.msg_type, jd_head.pb_msg.cmd)
        if const.RPC_TYPE_REQUEST == jd_head.pb_msg.msg_type and const.RPC_CMD == jd_head.pb_msg.cmd:
            RpcProcess.RpcRpcPacket(input, jd_head)
        else:
            self.ProcJdPacket(slot, input, jd_head)

        return 0

    def SendJdPacket(self, outPkg):
        return self.curr_slot.SendPacket(outPkg)


class ServerNode:

    game_node = None

    def __init__(self):
        pass

    def __del__(self):
        pass

    @classmethod
    def SetGameNode(cls, game):
        cls.game_node = game

    @classmethod
    def GetGameNode(cls):
        return cls.game_node


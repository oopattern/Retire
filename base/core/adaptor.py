# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：adaptor.py
# 日期：2017/3/1-17:22
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------

from const import *
from rpc_name import *
from log import *
from tcpclient import *
import rpc_channel
import dispatch_pb2
import name_pb2
from pb_msg import *

#msg_type
const.MsgType_Business  = 0x1
const.MsgType_Manage    = 0x2
const.MsgType_Broadcast = 0x3
const.MsgType_Multicast = 0x4

#command
const.CMD_DISPATCH_REG_TO_MASTER                    = 0x504 #dispatch向master注册
const.CMD_DISPATCH_GET_DISPATCH_LIST_FROM_MASTER    = 0x505 #dispatch获取到可连接的dispatch列表
const.CMD_BUSSINESS_GET_DIPATCH_FROM_MASTER         = 0x506 #业务服务从master获取一个供连接的dipatch
const.CMD_BUSSINESS_REG_TO_DISPATCH                 = 0x503
const.CMD_BUSSINESS_TURN                            = 0x507
const.CMD_RIGISTER_SRV_CHANNEL                      = 0x0510
const.CANCEL_RIGISTER_SRV_CHANNEL                   = 0x0511
const.CMD_DISPATCH_ADD_SERVICE                      = 0x0508
const.CMD_DISPATCH_REG_TO_NAME                      = 0x0520
const.CMD_SEND_ADD_SERVICE                          = 0x0521
const.CMD_SEND_DEL_SERVICE                          = 0x0522
const.CMD_BROADCAST_SERVICE_LIST                    = 0x0523
const.CMD_REQUEST_SYNC_SERVICE                      = 0x0524

#server_type
const.ServerType_None               = 0x00
const.ServerType_GamePlayer         = 0x01
const.ServerType_Hall               = 0x02
const.ServerType_Alloc              = 0x03
const.ServerType_User               = 0x04
const.ServerType_Room               = 0x05
const.ServerType_Broadcast          = 0x06
const.ServerType_Master             = 0x07
const.ServerType_Friend             = 0x08
const.ServerType_Log                = 0x09
const.ServerType_MemberCache        = 0x0A
const.ServerType_DbUpdate           = 0x0B
const.ServerType_UserInfoChache     = 0x0C
const.ServerType_Report             = 0x0D
const.ServerType_Dispatch           = 0x0E
const.ServerType_PHPNotify          = 0x0F
const.ServerType_PHPAgent           = 0x10
const.ServerType_ServiceManager     = 0x11
const.ServerType_RpcDispatch        = 0x12
const.ServerType_RpcMaster          = 0x13

class Adaptor:
    m_DispatchConn = None
    def __init__(self, game):
        self.m_Game = game
        self.m_MasterConn = None
        self.m_GameInfo = None

    def __del__(self):
        pass

    def InitAdaptor(self, master_info, game_info):
        self.m_GameInfo = game_info
        RpcName.RigisterSelfInfo(game_info["svid"], game_info["type"])
        self.m_MasterConn = CTcpClient(self.m_Game.m_Reactor, self.m_Game)
        self.m_MasterConn.SetType(const.ServerType_RpcMaster)
        self.m_MasterConn.SetId(master_info["svid"])
        ret = self.m_MasterConn.InitConnect(master_info["ip"], master_info["port"])
        if not ret:
            log_err("connect master fail:[%s:%d]",master_info["ip"], master_info["port"])

    def ProcBackConnect(self, connector):
        log_debug("adaptor:procbackconnect")
        ret = 0
        if connector.m_Type == const.ServerType_RpcMaster:
            ret = self.WantToGetDispatch(connector)
        elif connector.m_Type == const.ServerType_RpcDispatch:
            ret = self.RigisterToDispatch(connector)
        return ret

    def ProcBackPacket(self, connector, input_package, jd_head):
        log_debug("adaptor:procbackpacket")
        ret = 1
        if jd_head.pb_msg.msg_type == const.MsgType_Manage:
            if jd_head.pb_msg.cmd == const.CMD_BUSSINESS_GET_DIPATCH_FROM_MASTER:
                ret = self.GetDispatchFromServer(jd_head, input_package, connector)
            elif jd_head.pb_msg.cmd == const.CMD_BUSSINESS_REG_TO_DISPATCH:
                ret = self.CheckRigisteToDispatch(jd_head, input_package, connector)
            elif jd_head.pb_msg.cmd == const.CMD_BROADCAST_SERVICE_LIST:
                ret = self.ProcBroadcastServiceList(jd_head, input_package, connector)

        return ret

    def SendJdPacket(self, outPkg):
        self.m_DispatchConn.SendPacket(outPkg)

    def WantToGetDispatch(self, connector):
        log_debug("adaptor:wantogetdispatch")
        output = JDOutput()
        output.Begin()
        rpc_channel.PbHeadConstructor(output, const.CMD_BUSSINESS_GET_DIPATCH_FROM_MASTER, const.MsgType_Manage)
        output.End()
        connector.SendPacket(output)
        return 0

    @classmethod
    def GetDispacthcHandler(cls):
        return cls.m_DispatchConn

    def GetDispatchFromServer(self, jd_head, input_package, connector):
        log_debug("adaptor:getdispatchfromserver")
        body_buf  = input_package.ReadBinary()
        body = PbMessage(dispatch_pb2.DispatchInfo())
        if not body.Decode(body_buf):
            log_err("parse rpc body proto err!!!")
            return 0
        log_debug("ip:%s, port:%s, text:%s, buf:%s",body.pb_msg.ip, body.pb_msg.port, body.pb_msg, body_buf)
        Adaptor.m_DispatchConn = CTcpClient(self.m_Game.m_Reactor, self.m_Game)
        Adaptor.m_DispatchConn.SetType(const.ServerType_RpcDispatch)
        Adaptor.m_DispatchConn.SetId(body.pb_msg.svid)

        ret = Adaptor.m_DispatchConn.InitConnect(body.pb_msg.ip, body.pb_msg.port)
        if not ret:
            log_err("connect dispatch fail:[%s:%d]", body.pb_msg.ip, body.pb_msg.port)
            return 0
        log_debug("get dispatch ip : %s port: %s", body.pb_msg.ip, body.pb_msg.port)
        return 0

    def RigisterToDispatch(self, connector):
        log_debug("adaptor:rigstertodispatch")
        output = JDOutput()
        output.Begin()
        rpc_channel.PbHeadConstructor(output, const.CMD_BUSSINESS_REG_TO_DISPATCH, const.MsgType_Manage)
        req_msg = PbMessage(dispatch_pb2.BussinessSrvInfo())
        req_msg.pb_msg.srv_type = self.m_GameInfo["type"]
        req_msg.pb_msg.svid = self.m_GameInfo["svid"]
        req_msg.pb_msg.param = self.m_GameInfo["param"]
        req_str = req_msg.Encode()
        output.WriteBinary(req_str)
        output.End()
        connector.SendPacket(output)
        return 0

    def CheckRigisteToDispatch(self, jd_head, input_package, connector):
        log_debug("adaptor:checkrigistertodispatch")
        body_buf = input_package.ReadBinary()
        body = PbMessage(dispatch_pb2.DispatchRegMasterRsp())
        if not body.Decode(body_buf):
            log_err("parse rpc body proto err!!!")
        if body.pb_msg.ret == 1:
            log_err("Rigister To Dispatch lose")
        else:
            log_debug("Rigister To Dispatch success")
            self.RigisterToNameService(jd_head, connector)
        return 0

    def RigisterToNameService(self, jd_head, connector):
        log_debug("adaptor:rigistertonameservice")
        output = JDOutput()
        output.Begin()
        rpc_channel.PbHeadConstructor(output, const.CMD_SEND_ADD_SERVICE, const.MsgType_Manage)
        req_msg = PbMessage(name_pb2.PB_ServiceInfo())
        req_msg.pb_msg.srv_type = self.m_GameInfo["type"]
        req_msg.pb_msg.svid = self.m_GameInfo["svid"]
        req_msg.pb_msg.srv_name = self.m_GameInfo["name"]
        req_msg.pb_msg.srv_group = self.m_GameInfo["group_id"]
        req_msg.pb_msg.srv_dispatch = self.m_DispatchConn.m_Id
        req_msg.pb_msg.mod_key = self.m_GameInfo["mod_key"]
	req_msg.pb_msg.mod_count = self.m_GameInfo["mod_count"]
	req_msg.pb_msg.service_id = self.m_GameInfo["service_id"]
	req_str = req_msg.Encode()
        output.WriteBinary(req_str)
        output.End()
        connector.SendPacket(output)
        return 0

    def ProcBroadcastServiceList(self, jd_head, input_package, connector):
        log_debug("adaptor:procbroadcastservicelist")
        body_buf = input_package.ReadBinary()
        body = PbMessage(name_pb2.PB_ServiceList())
        if not body.Decode(body_buf):
            log_err("parse rpc body proto err!!!")
            return
        ret = RpcName.ReloadServiceList(body.pb_msg.service_list)
        return ret

    def Broadcast(self, connector, req_msg):
        outPkg = JDOutput()
        outPkg.Begin()
        rpc_channel.PbHeadConstructor(outPkg, const.CMD_BUSSINESS_TURN, const.MsgType_Broadcast)
        req_str = req_msg.Encode()
        outPkg.WriteBinary(req_str)
        outPkg.End()

    def MultiCast(self, cmd, req_msg):
        outPkg = JDOutput()
        outPkg.Begin()
        rpc_channel.PbHeadConstructor(outPkg, cmd, const.MsgType_Multicast)
        req_str = req_msg.Encode()
        outPkg.WriteBinary(req_str)
        outPkg.End()

    def RigisteChannel(self, connector, channel_name):
        outPkg = JDOutput()
        outPkg.Begin()
        rpc_channel.PbHeadConstructor(outPkg, const.CMD_RIGISTER_SRV_CHANNEL, const.MsgType_Manage)
        req_msg = PbMessage(dispatch_pb2.CChannel())
        req_msg.pb_msg.channel_name = channel_name
        req_str = req_msg.Encode()
        outPkg.WriteBinary(req_str)
        outPkg.End()
        connector.SendPacket(outPkg)









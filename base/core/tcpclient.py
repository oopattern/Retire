#localclient.py
# -*- coding: utf-8 -*-


from tcphandler import  *
from packet import *
from timer import *
from const import *
import time

const.ReconnectCnt = 10
const.ReconnectTimerId = 0 

class CTcpClient(CSocketHandler, CBYTimer):
 
    def __init__(self, reactor_, server_):
        CSocketHandler.__init__(self)
        CBYTimer.__init__(self)
        self.m_Reactor = reactor_
        self.m_PacketParser = reactor_.GetPacketParser()
        self.m_Server = server_
        self.m_IsConnected = False
        self.m_ReconnectCnt = 0

    def __del__(self):
        self.m_Server = None
        self.m_IsConnected = False

    def Destroy(self):
        core_err("destory")
        self.m_Server = None
        self.m_IsConnected = False
        CSocketHandler.Destroy(self)

    def OnConnected(self):
        self.m_IsConnected = True
        print('lidi what the fuck!!!')
        self.m_Server.OnBackConnected(self)
        return 0

    def OnClose(self):
        print('lidi awesome!!!')
        core_err("on close")
        self.m_IsConnected = False
        return self.m_Server.OnBackClose(self)

    def Reconnect(self, time = 5, isloop = True):
        core_debug("reconnect")
        self.Reset()
        if self.Connect() is False:
            self.StartTimer(1001,time, isloop)
        else:
            return True

    def Connect(self):
        try:
            self.m_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.m_Socket.connect((self.m_Ip, self.m_Port))
            core_info("Reconnect [%s:%d] success!", self.m_Ip, self.m_Port)
        except IOError as err:
            core_err("Reconnect [%s:%d] failed! err_no:%d, err_msg:%s", self.m_Ip, self.m_Port, err.errno, os.strerror(err.errno))
            return False
        self.m_ReconnectCnt = 0
        self.m_IsConnected = True
        self.m_Socket.setblocking(0)
        self.EnableInput()
        self.DisableOutput()
        self.AttachPoller(self.m_Reactor.GetPollerUnit())
        return True

    def OnTimerOut(self, timer_id):
        if timer_id is const.ReconectTimerId:
            if self.m_ReconnectCnt >= const.ReconectCnt:
                core_err("server [%s:%d] core: cnt:%s", self.m_Ip, self.m_Port, self.m_ReconnectCnt)
                self.StopTimer(const.ReconectTimerId)
                return False
            else:
                self.m_ReconnectCnt += 1
            if self.Connect() is True:
                self.StopTimer(const.ReconectTimerId)
                return True
            else:
                return False

    def OnPacketComplete(self, buf_list):
        print('lidi ri le gou le')
        input_pkg = InputPacket()
        input_pkg.CopyFromListBuf(buf_list)

        ret = self.m_Server.ProccessBackPacket(self, input_pkg)
        return ret

    def OnJdPacketComplete(self, buf_list):
        input_pkg = InputPacket()
        input_pkg.CopyFromListBuf(buf_list)
        ret = self.m_Server.ProcessJdPacket(self, input_pkg)
        return ret

    def InitConnect(self, ip_, port_):
        self.SetIp(ip_)
        self.SetPort(port_)
        self.m_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.m_Socket.connect((ip_, port_))
        except IOError as err:
            core_err("Connect [%s:%d] Failed,err_no=%d, err_str=%s ",
                     str(ip_), port_, err.errno, os.strerror(err.errno))
            self.HandleClose()
            return  False


        self.m_Socket.setblocking(0)
        self.EnableInput()
        self.DisableOutput()
        self.AttachPoller(self.m_Reactor.GetPollerUnit())

        ret = self.OnConnected()
        if(ret < 0):
            return  False

        return  True

    def SendPacket(self, outPkg):
        if(not self.m_IsConnected):
            self.Reset()
            if self.Connect() is True:
                return self.SendBuf(outPkg.PacketListBuf())
            else:
                return -1
        else:
            return self.SendBuf(outPkg.PacketListBuf())
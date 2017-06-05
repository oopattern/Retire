#udphandler.py
# -*- coding: utf-8 -*-


from poller import *
import socket

class CUdpClient(CBasePoller):
    def __init__(self, reactor_, server_):
        CBasePoller.__init__(self)
        self.m_Ip = ''
        self.m_Port = 0
        self.m_Reactor = reactor_
        self.m_Server = server_

    def __del__(self):
        CBasePoller.__del__(self)

    def Destroy(self):
        self.DisableInput()
        self.DisableOutput()
        self.DetachPoller()
        if(self.m_Socket is not  None):
            self.m_Socket.close()
        self.m_Socket = None
        CBasePoller.Destroy(self)

    def Reset(self):
        self.DisableInput()
        self.DisableOutput()
        self.DetachPoller()
        if(self.m_Socket is not  None):
            self.m_Socket.close()
        self.m_Socket = None


    def GetIp(self):
        return self.m_Ip

    def SetIp(self, ip_):
        self.m_Ip = ip_

    def GetPort(self, ):
        return  self.m_Port

    def SetPort(self, port_):
        self.m_Port = port_

    def NetFD(self):
        if(self.m_Socket is None):
            return  -1
        else:
            return self.m_Socket.fileno()

    def ProEvent(self, nEvent):
        if(nEvent & const.POLL_EVENT_READ):
            return  self.ProReadEvent()
        elif (nEvent & const.POLL_EVENT_WRITE):
            self.DisableOutput()
            return  const.POLLER_SUCC
        elif (nEvent & const.POLL_EVENT_CLOSE):
            return self.ProCloseEvent()

    def ProCloseEvent(self):
        ret  = self.HandleClose()
        return  const.POLLER_COMPLETE

    def HandleClose(self):
        ret = self.m_Server.OnUdpClientClose(self)
        if(ret > 0):
            self.Reset()
        else:
            self.Destroy()

    def InitConnect(self, ip_, port_):
        self.SetIp(ip_)
        self.SetPort(port_)
        self.m_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.m_Socket.connect((ip_, port_))
        except IOError as err:
            core_err("Connect [%s:%d] Failed, errno=%d, err_str=%s ",
                     str(ip_), port_, err.errno, os.strerror(err.errno))

        self.m_Socket.setblocking(0)
        self.EnableInput()
        self.DisableOutput()
        self.AttachPoller(self.m_Reactor.GetPollerUnit())

    def ProReadEvent(self):
        self.HandleInput()
        return  const.POLLER_SUCC

    def HandleInput(self):
        try:
            str_buf = self.m_Socket.recv(8192)
        except IOError as err:
            if (err.errno == errno.EINTR):
                print ("errno.EINTR ", os.strerror(err.errno))
                return
            elif (err.errno == errno.EAGAIN):
                print ("errno.EAGAIN ", os.strerror(err.errno))
                return
            else:
                print ("upd client recv Unkonw Err, ", os.strerror(err.errno))
                self.m_Server.OnUdpClientClose(self)
                return
        self.m_Server.ProcUdpClientPacket(self, str_buf)

    def SendPacket(self, outPkg):
        list_buf = outPkg.PacketListBuf()
        str_buf = ''.join(list_buf)
        self.SendStrBuf(str_buf)


    def SendStrBuf(self, str_buf):
        try:
            ret = self.m_Socket.send(str_buf)
        except IOError as err:
            if (err.errno == errno.EINTR):
                core_err("errno.EINTR  errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
            elif (core_err.errno == errno.EAGAIN):
                core_err("errno.EAGAIN errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
            else:
                core_err("upd send Unkonw Err, errno=%d, strerror=%s", err.errno, os.strerror(err.errno))
                self.m_Server.OnUdpClientClose(self)



#listener.py
# -*- coding: utf-8 -*-

from poller import *
from clienthandler import *

class CTcpListener(CBasePoller):
    def __init__(self, reactor_, server_):
        CBasePoller.__init__(self)
        self.m_Ip = ''
        self.m_Port = 0
        self.m_Backlog = 0
        self.m_Socket = None
        self.m_Reactor = reactor_
        self.m_PacketParser = reactor_.GetPacketParser()
        self.m_Server = server_
        self.m_ConnTable = {}

    def __del__(self):
        if self.m_Socket  is not  None:
            self.m_Socket.close()
        self.m_Ip = ''
        self.m_Port = 0
        self.m_Backlog = 0
        self.m_Socket = None
        self.m_Reactor = None
        self.m_PacketParser = None
        self.m_Server = None
        CBasePoller.__del__(self)

    def Destroy(self):
        pass

    FlowId = 1

    def NetFD(self):
        if(self.m_Socket is None):
            return  -1
        else:
            return self.m_Socket.fileno()

    def SetPacketParser(self, packet_parser):
        self.m_PacketParser = packet_parser

    def GetConnHandler(self, handler_id):
        if(self.m_ConnTable.has_key(handler_id)):
            return self.m_ConnTable[handler_id]
        else:
            return  None

    def Listen(self, ip_, port_, backlog_):
        self.m_Ip = ip_
        self.m_Port = port_
        self.m_Backlog = backlog_

        try:
            self.m_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.m_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.m_Socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            self.m_Socket.bind((self.m_Ip, self.m_Port))
            self.m_Socket.listen(self.m_Backlog)
            self.m_Socket.setblocking(0)
            self.EnableInput()
            self.DisableOutput()
        except IOError as err:
            core_boot ("listen [%s:%d] fail !! errno=%d, err_str=%s ", ip_, port_, err.errno, os.strerror(err.errno))
            self.m_Socket.close()
            return  False
        except:
            core_boot ("listen [%s:%d] fail !! unknow err ", ip_, port_)
            self.m_Socket.close()
            return  False

        if(self.AttachPoller(self.m_Reactor.GetPollerUnit()) < 0):
            self.m_Socket.close()
            core_boot ("listen [%s:%d] AttachPoller fail !!  ", ip_, port_)
            return  False

        core_boot ("listen tcp port [%s:%d] success!!", ip_, port_)
        return  True


    def ProEvent(self, nEvent):
        if(nEvent & const.POLL_EVENT_READ):
            return  self.ProReadEvent()
        elif (nEvent & const.POLL_EVENT_WRITE):
            return  self.ProWriteEvent()
        elif (nEvent & const.POLL_EVENT_CLOSE):
            return self.ProCloseEvent()

        return const.POLLER_SUCC

    def ProWriteEvent(self):
        self.DisableOutput()
        return  const.POLLER_SUCC

    def ProCloseEvent(self):
        self.DetachPoller()
        err = "listen port socket err, [%s:%d]" % (self.m_Ip, self.m_Port)
        core_err(err)
        raise Exception(err)

    def ProReadEvent(self):
        self.ProAccept()
        return  const.POLLER_SUCC

    def ProAccept(self):
        while(True):
            try:
                conn_sock, address = self.m_Socket.accept()
            except IOError as err:
                if(err.errno == errno.EINTR):
                    core_err ("errno.EINTR  errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
                    continue
                elif(err.errno == errno.EAGAIN):
                    core_err ("errno.EAGAIN errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
                    return
                else:
                    core_err (" accept Unkonw Err, errno=%d, strerror=%s", err.errno, os.strerror(err.errno))
                    return

            connHandler = CClientHandler()
            connHandler.SetIp(address[0])
            connHandler.SetPort(address[1])
            connHandler.m_Socket = conn_sock
            connHandler.m_Socket.setblocking(0)
            connHandler.m_PacketParser = self.m_PacketParser
            connHandler.m_Listener = self
            connHandler.m_Server = self.m_Server
            connHandler.EnableInput()
            connHandler.DisableOutput()

            self.FlowId = (self.FlowId + 1) % 0xFFFFF
            self.m_ConnTable[self.FlowId] = connHandler
            connHandler.m_HandlerId = self.FlowId

            if(connHandler.OnConnected() < 0):
                connHandler.HandleClose()
                continue

            if(connHandler.AttachPoller(self.GetPollerUnit()) < 0):
                connHandler.HandleClose()
                continue

            core_boot("accept new handler, handler_id=%d, addr=[%s:%d] ", self.FlowId, address[0], address[1])


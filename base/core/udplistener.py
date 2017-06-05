#udplistener.py
# -*- coding: utf-8 -*-

from poller import *


class CUdpListener(CBasePoller):
    def __init__(self, reactor_, server_):
        CBasePoller.__init__(self)
        self.m_Ip = ''
        self.m_Port = 0
        self.m_Socket = None
        self.m_Reactor = reactor_
        self.m_PacketParser = reactor_.GetPacketParser()
        self.m_Server = server_


    def __del__(self):
        if self.m_Socket  is not  None:
            self.m_Socket.close()
        self.m_Ip = ''
        self.m_Port = 0
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


    def Listen(self, ip_, port_):
        self.m_Ip = ip_
        self.m_Port = port_

        try:
            self.m_Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.m_Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.m_Socket.bind((self.m_Ip, self.m_Port))
            self.m_Socket.setblocking(0)
            self.EnableInput()
            self.DisableOutput()
        except IOError as err:
            core_boot ("udp listen [%s:%d] fail !! err_str=%s ", ip_, port_, os.strerror(err.errno))
            self.m_Socket.close()
            return  False
        except:
            core_boot ("udp listen [%s:%d] fail !! unknow err ", ip_, port_)
            self.m_Socket.close()
            return  False

        if(self.AttachPoller(self.m_Reactor.GetPollerUnit()) < 0):
            self.m_Socket.close()
            core_boot ("udp listen [%s:%d] AttachPoller fail !!  ", ip_, port_)
            return  False

            core_boot("listen udp port [%s:%d] success!!", ip_, port_)
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
        self.HandleInput()
        return  const.POLLER_SUCC

    def HandleInput(self):
        try:
            str_buf, remote_addr = self.m_Socket.recvfrom(8192)
        except IOError as err:
            if (err.errno == errno.EINTR):
                core_err("errno.EINTR  errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
                return
            elif (err.errno == errno.EAGAIN):
                core_err("errno.EAGAIN errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
                return
            else:
                core_err(" accept Unkonw Err, errno=%d, strerror=%s", err.errno, os.strerror(err.errno))
                return

        self.m_Server.ProcUdpListenerPacket(self, str_buf, remote_addr)

    def SendPacket(self, outPkg, addr_):
        list_buf = outPkg.PacketListBuf()
        str_buf = ''.join(list_buf)
        self.SendStrBuf(str_buf, addr_)

    def SendStrBuf(self, str_buf, addr_):
        try:
            self.m_Socket.sendto(str_buf, addr_)
        except IOError as err:
            if (err.errno == errno.EINTR):
                core_err("errno.EINTR  errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
            elif (err.errno == errno.EAGAIN):
                core_err("errno.EAGAIN errno=%d, strerror=%s ", err.errno, os.strerror(err.errno))
            else:
                core_err("upd send Unkonw Err, errno=%d, strerror=%s", err.errno, os.strerror(err.errno))



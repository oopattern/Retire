#sockethandler.py
# -*- coding: utf-8 -*-

from poller import *
import socket

const.CONN_IDLE = 0
const.CONN_FATAL_ERROR  = 1
const.CONN_CONNECTING = 3
const.CONN_DISCONNECT = 4
const.CONN_CONNECTED = 5
const.CONN_DATA_SENDING = 6
const.CONN_DATA_RECVING = 7
const.CONN_SEND_DONE = 8
const.CONN_RECV_DONE = 9



class CSocketHandler(CBasePoller):
    def __init__(self):
        CBasePoller.__init__(self)
        self.m_Id = -1
        self.m_Type = 0
        self.m_Property_int = 0
        self.m_Property_obj = None
        self.m_Socket = None
        self.m_PacketParser = None
        self.m_ReadCache = []
        self.m_WriteCache = []
        self.m_Ip = ''
        self.m_Port = 0

    def __del__(self):
        CBasePoller.__del__(self)

    def Destroy(self):
        self.DetachPoller()
        self.m_Property_obj = None
        if(self.m_Socket is not None):
            self.m_Socket.close()
        self.m_Id = None
        self.m_Type = None
        self.m_Property_int = None
        self.m_Property_obj = None
        self.m_Socket = None
        self.m_PacketParser = None
        self.m_ReadCache = None
        self.m_WriteCache = None
        self.m_Ip = None
        self.m_Port = None
        CBasePoller.Destroy(self)

    def Reset(self):
        self.DisableInput()
        self.DisableOutput()
        self.m_ReadCache = []
        self.m_WriteCache = []
        self.DetachPoller()
        if(self.m_Socket is not  None):
            self.m_Socket.close()
        self.m_Socket = None


    def OnClose(self):
        raise Exception("abstractmethod")

    def OnConnected(self):
        raise Exception("abstractmethod")

    def OnPacketComplete(self, buf_list):
        raise Exception("abstractmethod")

    def OnJdPacketComplete(self, buf_list):
        raise Exception("abstractmethod")

    def GetSocket(self):
        return  self.m_Socket

    def SetSocket(self, socket_obj):
        self.m_Socket = socket_obj

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

    def GetId(self):
        return self.m_Id

    def SetId(self, id_):
        self.m_Id = id_

    def GetType(self):
        return  self.m_Type

    def SetType(self, type_):
        self.m_Type = type_

    def GetProperty(self):
        return  self.m_Property_int

    def SetProperty(self, data_):
        self.m_Property_int = data_

    def GetPropertyObj(self):
        return  self.m_Property_obj

    def SetPropertyObj(self, obj_):
        self.m_Property_obj = obj_

    def ProEvent(self, nEvent):
        if(nEvent & const.POLL_EVENT_READ):
            return  self.ProReadEvent()
        elif (nEvent & const.POLL_EVENT_WRITE):
            return  self.ProWriteEvent()
        elif (nEvent & const.POLL_EVENT_CLOSE):
            return self.ProCloseEvent()

        return const.POLLER_SUCC

    def ProReadEvent(self):
        ret = self.HandleInput()
        if(ret == const.CONN_RECV_DONE or ret == const.CONN_DATA_RECVING):
            return  const.POLLER_SUCC
        else:
            self.HandleClose()
            return  const.POLLER_FAIL


    def ProWriteEvent(self):
        ret = self.HandleOutput()
        if(ret == const.CONN_DATA_SENDING or ret == const.CONN_SEND_DONE):
            return  const.POLLER_SUCC
        else:
            # close handle by POLL_EVENT_READ or POLL_EVENT_CLOSE
            #self.HandleClose()
            return const.POLLER_FAIL

    def ProCloseEvent(self):
        ret  = self.HandleClose()
        return  const.POLLER_COMPLETE

    def SendBuf(self, buf_list):
        buf_len = len(buf_list)
        if(self.m_Socket is None or self.m_Socket.fileno() <= 0):
            self.m_WriteCache.extend(buf_list)
            buf_len = len(self.m_WriteCache)
            if(buf_len > 20*1024):
                self.m_WriteCache= []
            return  0

        if(0 == len(self.m_WriteCache)):
            str_buf = ''.join(buf_list)
            try:
                ret = self.m_Socket.send(str_buf)
            except IOError as err:
                if(err.errno == errno.EINTR or
                   err.errno == errno.EAGAIN or
                   err.errno == errno.EINPROGRESS):
                    self.m_WriteCache.extend(buf_list)
                    self.EnableOutput()
                    self.ApplyEvents()
                    return  0
                else:
                    # send err, do nothing
                    core_err("errno=%d, err_str=%s, strerror=%s ", err.errno, os.strerror(err.errno), err.strerror)
                    return -1
            if(ret < buf_len):
                self.m_WriteCache.extend(buf_list[ret:])
                self.EnableOutput()
                self.ApplyEvents()
                return  ret
            else:
                return  ret
        else:
            self.m_WriteCache.extend(buf_list)
            self.EnableOutput()
            self.ApplyEvents()
            return  0

    def SendPacket(self, outPkg):
        return  self.SendBuf(outPkg.PacketListBuf())

    def HandleClose(self):
        ret = self.OnClose()
        if(ret < 0):
            self.Reset()
        elif ret > 0:
            pass
        else:
            self.Destroy()

    def HandleInput(self):
        try:
            str_buf = self.m_Socket.recv(8192)
        except IOError as err:
            if( err.errno == errno.EINTR or err.errno == errno.EAGAIN ):
                return const.CONN_DATA_RECVING
            else:
                core_err("socket.recv err fd=%d, errno=%d, err_str=%s",
                         self.m_Socket.fileno(), err.errno, os.strerror(err.errno))
                return const.CONN_FATAL_ERROR
        if('' == str_buf):
            return const.CONN_DISCONNECT
        else:
            self.m_ReadCache.extend(list(str_buf))
            #print( 'self.m_ReadCache=', ','.join(map(lambda x: hex(ord(x)), self.m_ReadCache)))
            conn_state = const.CONN_FATAL_ERROR
            while(len(self.m_ReadCache) > 0):
                packet_len = self.m_PacketParser.ParsePacket(self.m_ReadCache)
                if(packet_len < 0):
                    self.DisableInput()
                    return const.CONN_FATAL_ERROR
                elif (packet_len == 0):
                    return const.CONN_DATA_RECVING
                else:
                    if(self.m_PacketParser.m_proctol == const.JD_PROTOCOL):
                        ret = self.OnJdPacketComplete(self.m_ReadCache[0:packet_len])
                    else:
                        ret = self.OnPacketComplete(self.m_ReadCache[0:packet_len])
                    if(ret < 0):
                        return  const.CONN_FATAL_ERROR

                    self.m_ReadCache = self.m_ReadCache[packet_len:]
                    conn_state = const.CONN_RECV_DONE

            return  conn_state


    def HandleOutput(self):
        buf_len = len(self.m_WriteCache)
        if( buf_len > 0):
            str_buf = ''.join(self.m_WriteCache)
            try:
                ret = self.m_Socket.send(str_buf)
            except IOError as err:
                if (err.errno == errno.EINTR or
                    err.errno == errno.EAGAIN or
                    err.errno == errno.EINPROGRESS):
                    self.EnableOutput()
                    self.ApplyEvents()
                    return const.CONN_DATA_SENDING
                else:
                    self.DisableOutput()
                    self.ApplyEvents()
                    return const.CONN_FATAL_ERROR

            if (ret < buf_len):
                self.m_WriteCache = self.m_WriteCache[ret:]
                self.EnableOutput()
                self.ApplyEvents()
                return const.CONN_DATA_SENDING
            else:
                self.DisableOutput()
                self.ApplyEvents()
                self.m_WriteCache = []
                return const.CONN_SEND_DONE
        else:
            self.DisableOutput()
            self.ApplyEvents()
            return  const.CONN_FATAL_ERROR










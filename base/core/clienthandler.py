#clienthandler.py
# -*- coding: utf-8 -*-

from tcphandler import  *
from tcplistener import *
from packet import *

class CClientHandler(CSocketHandler):
    def __init__(self):
        CSocketHandler.__init__(self)
        self.m_HandlerId = -1
        self.m_Listener = None
        self.m_server = None
        core_debug("new client_handler obj", str(self))

    def __del__(self):
        CSocketHandler.__del__(self)
        core_debug("del client_handler obj", str(self))

    def Destroy(self):
        core_debug ("Destroy handler_id=", str(self.m_HandlerId))
        del self.m_Listener.m_ConnTable[self.m_HandlerId]
        self.m_HandlerId = None
        self.m_Listener = None
        self.m_Server = None
        CSocketHandler.Destroy(self)

    def OnConnected(self):
        #do nothing
        return 0

    def OnClose(self):
        return self.m_Server.OnClose(self)

    def OnPacketComplete(self, buf_list):
        input_pkg = InputPacket()
        input_pkg.CopyFromListBuf(buf_list)

        ret = self.m_Server.ProcessPacket(self, input_pkg)
        return ret

    def OnJdPacketComplete(self, buf_list):
        input_pkg = InputPacket()
        input_pkg.CopyFromListBuf(buf_list)

        ret = self.m_Server.ProcessJdPacket(self, input_pkg)
        return ret

#baseserver.py
# -*- coding: utf-8 -*-


from  packet import  *
import os, time, signal



class CBaseServer:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def Destroy(self):
        pass

    def InitServer(self):
        return 0

    def OnClose(self, client_handler):
        return 0

    def ProcessPacket(self, client_handler, input_pkg):
        return 0

    def ProcessJdPacket(self, client_handler, input_pkg):
        return 0

    def OnBackClose(self, back_client):
        return 0

    def OnBackConnected(self, back_client):
        return 0

    def ProccessBackPacket(self, back_client, input_pkg):
        return 0

    def ProcUdpListenerPacket(self, udp_listener, str_buf, remote_addr):
        return 0

    def ProcUdpClientPacket(self, udp_client, str_buf):
        return 0

    def OnUdpClientClose(self, udp_client):
        return 0

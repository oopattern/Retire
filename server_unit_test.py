#server_unit_test.py
# -*- coding: utf-8 -*-


import sys, os, time, datetime
sys.path.append("base/core")
from baseserver import *


class TestServer(CBaseServer):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def InitServer(self):
        print('lidi TestServer init')
        return 0

    def OnClose(self, client_handler):
        print("OnClose handler=", client_handler)
        return 0

    def ProcessPacket(self, client_handler, input_pkg):
        cmd = input_pkg.GetCmd()
        print ("ProcessPacket cmd=0x", hex(cmd))
        if(0x111 == cmd):
            num = input_pkg.ReadInt32()
            str_buf = input_pkg.ReadString()
            print("ProcessPacket ", num, str_buf)
            client_handler.SendPacket(input_pkg)
        else:
            # echo rcv packet
            client_handler.SendPacket(input_pkg)
        return 0

    def OnBackClose(self, back_client):
        print("OnBackClose client=", back_client)
        return 0

    def OnBackConnected(self, back_client):
        print "OnBackConnected, obj=%s"%back_client
        outPkg = OutPacket()
        outPkg.Begin(0x111)
        outPkg.WriteInt32(123)
        outPkg.WriteString("hello oopattern!!!")
        outPkg.End()
        back_client.SendPacket(outPkg)
        return 0

    def ProccessBackPacket(self, back_client, input_pkg):
        print('lidi ProccessBackPacket: please handle it')
        cmd = input_pkg.GetCmd()
        print ("ProccessBackPacket cmd=0x", hex(cmd))
        if(0x111 == cmd):
            num = input_pkg.ReadInt32()
            str_buf = input_pkg.ReadString()
            print("ProccessBackPacket ",  num, str_buf)
        elif (0x1122 == cmd):
            str_buf = input_pkg.ReadString()
            print("ProccessBackPacket str=",  str_buf)
        return 0
    
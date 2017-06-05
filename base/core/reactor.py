#poller.py
# -*- coding: utf-8 -*-

import traceback
from poller import *
from packet import *
import timer
from singleton import *
from const import *

class CReactor():
    def __init__(self):
        if platform.system() == "Windows":
            print('lidi ni niu----')
            self.m_PollerUnit = CWindowsPollerUint()
        else:
            self.m_PollerUnit = CPollerUnit()

        self.m_TimerUnit = timer.CTimerUnit()

    def __del__(self):
        self.m_PollerUnit = None
        self.m_PacketParser = None
        self.m_TimerUnit = None

    def Destroy(self):
        self.m_PollerUnit = None
        self.m_PacketParser = None
        self.m_TimerUnit = None

    @classmethod
    def Instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = CReactor()
        return cls._instance

    def SetPacketParser(self, packet_parser):
        self.m_PacketParser = packet_parser

    def GetPollerUnit(self):
        return  self.m_PollerUnit

    def GetTimerUnit(self):
        return self.m_TimerUnit

    def GetPacketParser(self):
        return self.m_PacketParser

    def RunEventLoop(self):
        try:
            while(True):
                self.m_PollerUnit.WaitPollerEvents(self.m_TimerUnit.ExpireMinSeconds(0.3))
                self.m_TimerUnit.CheckExpired()
                self.m_TimerUnit.CheckPending()
        except:
            trac = traceback.format_exc()
            core_err("core_down")
            core_err("trace_back= %s", trac)




#poller.py
# -*- coding: utf-8 -*-

import sys, os, socket, select, errno, platform, time
from abc import abstractmethod
from abc import ABCMeta
from const import *
from log import *

if platform.system() != "Windows":
    from select import epoll, EPOLLHUP, EPOLLERR, EPOLLIN, EPOLLOUT
else:
    EPOLLIN = 1
    EPOLLOUT = 4
    EPOLLERR = 8
    EPOLLHUP = 16


const.POLL_EVENT_CLOSE = (EPOLLHUP | EPOLLERR)
const.POLL_EVENT_READ = EPOLLIN
const.POLL_EVENT_WRITE = EPOLLOUT

const.POLLER_FAIL     = -2
const.POLLER_COMPLETE = -1
const.POLLER_SUCC     = 0


class CBasePoller:
    def __init__(self):
        self.newEvents = 0
        self.oldEvents = 0
        self.ownerUnit = None

    def __del__(self):
        self.newEvents = 0
        self.oldEvents = 0
        self.ownerUnit = None

    def Destroy(self):
        self.DetachPoller()

    def NetFD(self):
        raise Exception("abstractmethod")

    def ProEvent(self, nEvent):
        raise Exception("abstractmethod")

    def GetPollerUnit(self):
        return self.ownerUnit

    def EnableInput(self):
        self.newEvents |= EPOLLIN

    def EnableOutput(self):
        self.newEvents |= EPOLLOUT

    def DisableInput(self):
        self.newEvents &= ~EPOLLIN

    def DisableOutput(self):
        self.newEvents &= ~EPOLLOUT

    def ApplyEvents(self):
        if((self.ownerUnit is None ) or (self.oldEvents == self.newEvents)):
            return  0

        ret = self.ownerUnit.ModifyPollerEvent(self, self.newEvents)
        if(ret >= 0):
            self.oldEvents = self.newEvents
        return ret

    def AttachPoller(self, poller_unit):
        if(poller_unit is None):
            return  -1

        if self.ownerUnit is not None:
            if(self.ownerUnit is poller_unit):
                return 0
            else:
                self.DetachPoller()

        self.ownerUnit = poller_unit
        if self.NetFD() <= 0:
            return  -1  # err fd

        ret = poller_unit.AddPollerEvent(self, self.newEvents)
        if(ret >= 0):
            self.oldEvents = self.newEvents

        return  ret

    def DetachPoller(self):
        if(self.ownerUnit is None):
            return

        self.ownerUnit.DelPollerEvent(self)
        self.ownerUnit = None
        self.newEvents = 0
        self.oldEvents = 0


class CPollerUnit:
    def __init__(self):
        self.poller = epoll(1024*20)
        self.pollerTable = {}

    def __del__(self):
        for key,value in self.pollerTable.items():
            value.DetachPoller()

        self.pollerTable.clear()
        self.poller.close()
        self.poller = None


    def AddPollerEvent(self, poller_obj, eventmask):
        try:
            self.poller.register(poller_obj.NetFD(), eventmask)
        except IOError as err:
            core_err("errno=%d, err_str=%s, strerror=%s ", err.errno, os.strerror(err.errno), err.strerror)
            return  -1

        self.pollerTable[poller_obj.NetFD()] = poller_obj
        return  0

    def ModifyPollerEvent(self, poller_obj, eventmask):
        try:
            self.poller.modify(poller_obj.NetFD(), eventmask)
        except IOError as err:
            core_err("errno=%d, err_str=%s, strerror=%s ", err.errno, os.strerror(err.errno), err.strerror)
            return -1
        return 0

    def DelPollerEvent(self, poller_obj):
        try:
            self.poller.unregister(poller_obj.NetFD())
            del self.pollerTable[poller_obj.NetFD()]
        except IOError as err:
            core_err("errno=%d, err_str=%s, strerror=%s ", err.errno, os.strerror(err.errno), err.strerror)

        return  0

    def WaitPollerEvents(self, timeout_seconds_float):
        if timeout_seconds_float is None:
            timeout_seconds_float = 0.3  # Wait 0.3 second

        try:
            nEvents = self.poller.poll(timeout_seconds_float)
        except IOError as err:
            core_err("errno=%d, err_str=%s, strerror=%s", err.errno,  os.strerror(err.errno), err.strerror)
            if err.errno == errno.EINTR:
                return
            else:
                raise err

        for fd, event in nEvents:
            if(not self.pollerTable.has_key(fd)):
                # wild fd, can't find the poller_object
                # so, remove from poller_unit, provent the fd loop trigger event;
                core_err(" fd=%d, has no poller_object ", fd)
                self.poller.unregister(fd)
            else:
                poller_obj = self.pollerTable[fd]
                # poller_obj.newEvents = poller_obj.oldEvents

                if(event & (EPOLLHUP | EPOLLERR)):
                    poller_obj.ProEvent(const.POLL_EVENT_CLOSE)
                    continue

                if (event & EPOLLIN):
                    ret = poller_obj.ProEvent(const.POLL_EVENT_READ)
                    if(not self.pollerTable.has_key(fd)):
                        # poller_obj already delete in ProEvent
                        continue

                    if (ret != const.POLLER_SUCC):
                        continue

                if (event & EPOLLOUT):
                    ret = poller_obj.ProEvent(const.POLL_EVENT_WRITE)
                    if(not self.pollerTable.has_key(fd)):
                        # poller_obj  already delete in ProEvent
                        continue

                    if(ret != const.POLLER_SUCC):
                        continue

                poller_obj.ApplyEvents()



# Windows platform server, only for test
class CWindowsPollerUint(CPollerUnit):
    def __init__(self):
        #self.poller = epoll(1024)
        self.pollerTable = {}

    def __del__(self):
        pass


    def AddPollerEvent(self, poller_obj, eventmask):
        print('lidi make some noice1111')
        self.pollerTable[poller_obj.NetFD()] = poller_obj
        return 0


    def ModifyPollerEvent(self, poller_obj, eventmask):
        print('lidi make some noice22222')
        self.pollerTable[poller_obj.NetFD()] = poller_obj
        return 0


    def DelPollerEvent(self, poller_obj):
        print('lidi make some noice3333')
        del self.pollerTable[poller_obj.NetFD()]
        return 0


    def WaitPollerEvents(self, timeout_seconds_float):
        if timeout_seconds_float is None:
            timeout_seconds_float = 0.3  # Wait 0.5 second

        input_list = []
        output_list = []
        err_list = []
        ret_triple = ()

        for k, v in self.pollerTable.items():
            if (v.newEvents & EPOLLIN):
                input_list.append(v.m_Socket)
            if (v.newEvents & EPOLLOUT):
                 output_list.append(v.m_Socket)
            err_list.append(v.m_Socket)

        try:
            ret_triple  = select.select(input_list, output_list, err_list, timeout_seconds_float)
            self.DispatchEvent(ret_triple)
        except select.error, err:
            core_err("select.error err_code=%d, err_str=%s", err[0], os.strerror(err[0]))
            time.sleep(0.5)

    def DispatchEvent(self, ret_triple):
        readable = ret_triple[0]
        writeable = ret_triple[1]
        exceptional = ret_triple[2]

        exceptional_fdlist = []
        readable_fdlist = []
        writeable_fdlist = []

        for sock in exceptional:
            exceptional_fdlist.append(sock.fileno())

        for sock in readable:
            readable_fdlist.append(sock.fileno())

        for sock in writeable:
            writeable_fdlist.append(sock.fileno())

        for fd in exceptional_fdlist:
            if (self.pollerTable.has_key(fd)):
                poller_obj = self.pollerTable[fd]
                poller_obj.ProEvent(const.POLL_EVENT_CLOSE)

        for fd in readable_fdlist:
            if (self.pollerTable.has_key(fd)):
                poller_obj = self.pollerTable[fd]
                poller_obj.ProEvent(const.POLL_EVENT_READ)

        for fd in writeable_fdlist:
            if (self.pollerTable.has_key(fd)):
                poller_obj = self.pollerTable[fd]
                poller_obj.ProEvent(const.POLL_EVENT_WRITE)

#timer.py
# -*- coding: utf-8 -*-

import heapq
import time
import reactor



class CTimerUnit:
    def __init__(self):
        self.m_timerList = []
        self.m_pendingList = []
        heapq.heapify(self.m_timerList)
        pass

    def Distroy(self):
        self.m_timerList = None
        self.m_pendingList = None

    def CheckPending(self):
        while self.m_pendingList:
            timer = self.m_pendingList.pop()
            if timer:
                timer.ProcessOnTimerOut(timer.m_nTimerId)
        pass

    def CheckExpired(self):
        now = time.time()
        for idx in range(300):
            # max check count
            if len(self.m_timerList) > 0:
                timer_obj = self.m_timerList[0]
                if(now >= timer_obj.m_objexp):
                    timer_obj = heapq.heappop(self.m_timerList)
                    timer_obj.OnTimerOut()
                else:
                    # no timer expired
                    return
            else:
                # no timer obj
                return

    def ExpireMinSeconds(self, min_sec):
        if(len(self.m_timerList) > 0):
            now = time.time()
            min_time = self.m_timerList[0].m_objexp
            if(min_time > now):
                if ((min_time - now) > min_sec):
                    return  min_sec
                else:
                    return  (min_time - now)
            else:
                return 0
        return min_sec


    def AddTimer(self, timer_obj):
        if timer_obj not in self.m_timerList:
            heapq.heappush(self.m_timerList, timer_obj)
        else:
            heapq.heapify(self.m_timerList)

    def DisableTimer(self, timer_obj):
        try:
            self.m_timerList.remove(timer_obj)
        except:
            pass
        finally:
            heapq.heapify(self.m_timerList)

class CTimerObject:
    def __init__(self):
        self.m_objexp = 0
        self.m_TimerUnit = reactor.CReactor.Instance().GetTimerUnit()

    def __del__(self):
        pass

    def __cmp__(self, other):
        return cmp(self.m_objexp, other.m_objexp)


    def AddTimer(self):
        self.m_TimerUnit.AddTimer(self)

    def DisableTimer(self):
        self.m_TimerUnit.DisableTimer(self)

    def OnTimerOut(self, timer_id):
        pass

class CTimerOutEvent:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def Destroy(self):
        pass

    def OnTimerOut(self, timer_id):
        pass


class CTimer(CTimerObject):
    def __init__(self):
        CTimerObject.__init__(self)
        self.m_interval = 0
        self.m_bLoop = False
        self.m_nTimerId = 0
        self.m_TimerEvent = None

    def __del__(self):
        self.StopTimer()
        self.m_nTimerId = 0
        self.m_TimerEvent = None

    def Destroy(self):
        self.StopTimer()
        self.m_nTimerId = 0
        self.m_TimerEvent = None

    def StartTimer(self, interval, isloop=False):
        self.m_objexp = (time.time() + interval)
        self.m_interval = interval
        self.m_bLoop = isloop
        self.m_TimerUnit.AddTimer(self)

    def StopTimer(self):
        self.m_TimerUnit.DisableTimer(self)
        self.m_bLoop = False

    def OnTimerOut(self):
        if(self.m_bLoop):
            self.StartTimer(self.m_interval, self.m_bLoop)

        if self.m_TimerEvent is not None:
            self.m_TimerEvent.OnTimerOut(self.m_nTimerId)

    def SetTimerObj(self, timer_event, timer_id):
        self.m_nTimerId = timer_id
        self.m_TimerEvent = timer_event



class CBYTimer(CTimerOutEvent):
    def __init__(self):
        CTimerOutEvent.__init__(self)
        self.m_TimerList = {}

    def __del__(self):
        if(len(self.m_TimerList) > 0):
            for timer_obj in self.m_TimerList.values():
                timer_obj.obj.StopTimer()
                timer_obj.Destroy()
            self.m_TimerList.clear()

    def Destroy(self):
        if(len(self.m_TimerList) > 0):
            for timer_obj in self.m_TimerList.values():
                timer_obj.obj.StopTimer()
                timer_obj.Destroy()
            self.m_TimerList.clear()

    def OnTimerOut(self, timer_id):
        pass

    def StartTimer(self, timer_id, second_, is_loop):
        timer_obj = self.GetTimer(timer_id)
        timer_obj.StartTimer(second_, is_loop)


    def StopTimer(self, timer_id):
        timer_obj = self.GetTimer(timer_id)
        timer_obj.StopTimer()

    def GetTimer(self, timer_id):
        if self.m_TimerList.has_key(timer_id):
            return  self.m_TimerList[timer_id]
        else:
            obj = CTimer()
            obj.SetTimerObj(self, timer_id)
            self.m_TimerList[timer_id] = obj
            return  obj


    def DelTimerObj(self, timer_id):
        if self.m_TimerList.has_key(timer_id):
            obj = self.m_TimerList[timer_id]
            obj.StopTimer()
            obj.Destroy()
            del self.m_TimerList[timer_id]
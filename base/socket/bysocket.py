# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：socket.py
# 日期：2017/6/12-15:23
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
import sys
import socket
import select
sys.path.append('../protocol')
from packet import *

RECV_TIMEOUT_SEC = 2 # 接收超时时间，单位秒

class BYSocket:
    def __init__(self):
        self.m_socket = None
        self.m_Cache = []
        self.m_PacketParser = CPacketParser()
        pass

    def CreatSock(self, addr):
        try:
            self.m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.m_socket.connect(addr)
        except IOError as err:
            print 'creat err'

    def RequestData(self, packet, encrpyt=False):
        if encrpyt is True:
            self.m_socket.send(packet.PacketListBuf())
        else:
            send_buf = ''.join(packet.PacketListBuf())
            self.m_socket.send(send_buf)
        self.m_socket.setblocking(0)
        ready = select.select([self.m_socket], [], [], RECV_TIMEOUT_SEC)
        if ready[0]:
            buf = self.m_socket.recv(1024)
            if buf == ' ':
                print 'buf is None'
                return None
            else:
                self.m_Cache.extend(list(buf))
                packet_len = self.m_PacketParser.ParsePacket(self.m_Cache)
                if packet_len < 0:
                    print 'len < 0'
                    return None
                else:
                    input_pkg = InputPacket()
                    input_pkg.CopyFromListBuf(self.m_Cache[0:packet_len])
                    self.m_socket.close()
                    return input_pkg
        else:
            return None

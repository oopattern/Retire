#protocol.py
# -*- coding: utf-8 -*-

import sys
import struct
from const import *
sys.path.append("../lib")
from log import *

# 4  protocol
const.ERR_Protocol = 0
const.BY9_PROTOCOL = 1
const.CHESS_PROTOCOL = 2
const.QEV1_PROTOCOL = 3
const.QE_PROTOCOL = 4
const.JD_PROTOCOL = 5

global g_proctol
g_proctol = const.BY9_PROTOCOL


class INetHead:
    def __init__(self):
        self.str_buff = []

    def __del__(self):
        del self.str_buff

    def WriteHead(self, list_buff, cmd, cversion):
        raise Exception("abstractmethod")

    def WritePacketLen(self, list_buff):
        raise Exception("abstractmethod")

    def WriteCheckCode(self, list_buff, check_code):
        raise Exception("abstractmethod")

    def GetCmd(self, list_buff):
        raise Exception("abstractmethod")

    def GetSubCmd(self, list_buff):
        raise Exception("abstractmethod")   # olny chess

    def BodyLen(self, list_buff):
        raise Exception("abstractmethod")

    def GetCheckCode(self, list_buff):
        raise Exception("abstractmethod")

class BY9Head(INetHead) :
    def __init__(self):
        INetHead.__init__(self)
        self.len = 0             # short, 0,1,
        self.flag1 = ''          # ch, 2,
        self.flag2 = ''          # ch, 3,
        self.cVersion = 0        # byte, 4,
        self.subVersion = 0      # byte, 5,
        self.cmd = 0             # short, 6,7,
        self.checkcode = 0       # byte, 8,

    @classmethod
    def HeadLen(cls):
        return  9

    def CheckHead(self, list_buf):
        if('B' == list_buf[2]  and 'Y' == list_buf[3]):
            return True
        else:
            return False

    def ParsePacketLen(self, list_buf):
        return (2+self.BodyLen(list_buf))

    def WriteHead(self, list_buff, cmd, cversion):
        list_buff += list(struct.pack("!H", (self.HeadLen()&0xFFFF)))
        list_buff += list('B')
        list_buff += list('Y')
        list_buff += list(struct.pack("!B", (cversion&0xFF)))
        list_buff += list(struct.pack("!B", (cversion&0xFF)))
        list_buff += list(struct.pack("!H", (cmd&0xFFFF)))
        list_buff += list(struct.pack("!B", 0))    #checkcode

    def WritePacketLen(self, list_buff):
        nLen = len(list_buff)
        nLen -= 2
        str_len = list(struct.pack("!H", nLen))
        list_buff[0] = str_len[0]
        list_buff[1] = str_len[1]

    def GetCmd(self, list_buff):
        str_buff = ''.join(list_buff[0:9])
        num = struct.unpack_from('!H', str_buff, 6)
        return num[0]

    def GetSubCmd(self, str_buff):
        return 0

    def BodyLen(self, list_buff):
        str_buff = ''.join(list_buff[0:9])
        num = struct.unpack_from('!H', str_buff, 0)
        return num[0]

    def GetCheckCode(self, list_buff):
        str_buff = ''.join(list_buff[0:9])
        num = struct.unpack_from('!B',str_buff, 8)
        return num[0]

    def WriteCheckCode(self, list_buff, check_code):
        list_buff[8] = chr(check_code)


class ChessHead(INetHead):
    def __init__(self):
        INetHead.__init__(self)
        self.len = 0             # short, 0,1
        self.flag1 = ''          # ch, 2,
        self.flag2 = ''          # ch, 3,
        self.cVersion = 0        # byte, 4,
        self.subVersion = 0      # byte, 5,
        self.cmd = 0             # short, 6,7,
        self.checkcode = 0       # byte, 8
        self.sub_cmd = 0         # short, 9,10
        self.seq = 0             # short, 11,12,
        self.source = 0          # byte, 13

    @classmethod
    def HeadLen(cls):
        return  14

    def CheckHead(self, list_buf):
        if('B' == list_buf[2]  and 'Y' == list_buf[3]):
            return True
        else:
            return  False

    def ParsePacketLen(self, list_buf):
        return (2+self.BodyLen(list_buf))

    def WriteHead(self, list_buff, cmd, cversion):
        list_buff += list(struct.pack("!H", (self.HeadLen()&0xFFFF)))
        list_buff += list('B')
        list_buff += list('Y')
        list_buff += list(struct.pack("!B", (cversion&0xFF)))
        list_buff += list(struct.pack("!B", (cversion&0xFF)))
        list_buff += list(struct.pack("!H", (cmd&0xFFFF)))
        list_buff += list(struct.pack("!B", 0) )   #checkcode
        list_buff += list(struct.pack("!H", 0))
        list_buff += list(struct.pack("!H", 0))
        list_buff += list('1')#struct.pack("!B", 0)

    def WritePacketLen(self, list_buff):
        nLen = len(list_buff)
        nLen -= 2
        str_len = list(struct.pack("!H", nLen))
        list_buff[0] = str_len[0]
        list_buff[1] = str_len[1]

    def GetCmd(self, list_buff):
        str_buff = ''.join(list_buff[0:14])
        num = struct.unpack_from('!H', str_buff, 6)
        return num[0]

    def GetSubCmd(self, list_buff):
        str_buff = ''.join(list_buff[0:14])
        num = struct.unpack_from('!H', str_buff, 9)
        return num[0]

    def BodyLen(self, list_buff):
        str_buff = ''.join(list_buff[0:14])
        num = struct.unpack_from('!H', str_buff, 0)
        return num[0]

    def GetCheckCode(self, list_buff):
        str_buff = ''.join(list_buff[0:14])
        num = struct.unpack_from('!B',str_buff, 8)
        return num[0]

    def WriteCheckCode(self, list_buff, check_code):
        list_buff[8] = chr(check_code)


class QEV1Head(INetHead) :
    def __init__(self):
        INetHead.__init__(self)
        self.len = 0             # int 0,1,2,3
        self.flag1 = ''          # ch  4,
        self.flag2 = ''          # ch  5,
        self.cVersion = 0        # short 6,7,
        self.cmd = 0             # int   8,9,10,11,
        self.gameid = 0          # short 12,13,
        self.regionid = 0        # short 14,15,
        self.deviceid = 0        # byte  16,
        self.checkcode = 0       # byte  17,

    @classmethod
    def HeadLen(cls):
        return  18

    def CheckHead(self, list_buf):
        if('B' == list_buf[4]  and 'Y' == list_buf[5]):
            return True
        else:
            return False

    def ParsePacketLen(self, list_buf):
        return (4+self.BodyLen(list_buf))

    def WriteHead(self, list_buff, cmd, cversion):
        list_buff += struct.pack("!i", (self.HeadLen()&0xFFFFFFFF))
        list_buff += 'B'
        list_buff += 'Y'
        list_buff += struct.pack("!H", (cversion&0xFFFF)) #cVersion
        list_buff += struct.pack("!i", (cmd&0xFFFFFFFF))  #cmd
        list_buff += struct.pack("!H", 0)  #gameid
        list_buff += struct.pack("!H", 0)  #regionid
        list_buff += struct.pack("!B", 0)  #deviceid
        list_buff += struct.pack("!B", 0)  #checkcode

    def WritePacketLen(self, list_buff):
        nLen = len(list_buff)
        nLen -= 4
        str_len = struct.pack("!i", nLen)
        list_buff[0] = str_len[0]
        list_buff[1] = str_len[1]
        list_buff[2] = str_len[2]
        list_buff[3] = str_len[3]

    def GetCmd(self, list_buff):
        str_buff = ''.join(list_buff[0:18])
        num = struct.unpack_from('!i', str_buff, 8)
        return num[0]

    def GetSubCmd(self, list_buff):
        return 0

    def BodyLen(self, list_buff):
        str_buff = ''.join(list_buff[0:18])
        num = struct.unpack_from('!i', str_buff, 0)
        return num[0]

    def GetCheckCode(self, list_buff):
        str_buff = ''.join(list_buff[0:18])
        num = struct.unpack_from('!B',str_buff, 17)
        return num[0]

    def WriteCheckCode(self, list_buff, check_code):
        list_buff[17] = chr(check_code)


class QEHead(INetHead) :
    def __init__(self):
        INetHead.__init__(self)
        self.len = 0             # int 0,1,2,3
        self.flag1 = ''          # ch  4,
        self.flag2 = ''          # ch  5,
        self.cVersion = 0        # byte 6,
        self.nExtendLen = 0      # byte 7,
        self.cmd = 0             # int  8,9,10,11,
        self.gameid = 0          # short 12,13
        self.checkcode = 0       # byte  14,

    @classmethod
    def HeadLen(cls):
        return  15

    def CheckHead(self, list_buf):
        if('Q' == list_buf[4]  and 'E' == list_buf[5]):
            return True
        else:
            return  False

    def ParsePacketLen(self, list_buf):
        return (4+self.BodyLen(list_buf))

    def WriteHead(self, list_buff, cmd, cversion):
        list_buff += list(struct.pack("!I", (self.HeadLen()&0xFFFFFFFF)))
        list_buff += list('Q')
        list_buff += list('E')
        list_buff += list(struct.pack("!B", (cversion&0xFF))) #cVersion
        list_buff += list(struct.pack("!B", 0)) #nExtendLen
        list_buff += list(struct.pack("!I", (cmd&0xFFFFFFFF)))  #cmd
        list_buff += list(struct.pack("!H", 0))  #gameid
        list_buff += list(struct.pack("!B", 0))  #checkcode

    def WritePacketLen(self, list_buff):
        nLen = len(list_buff)
        nLen -= 4
        str_len = struct.pack("!i", nLen)
        list_buff[0] = str_len[0]
        list_buff[1] = str_len[1]
        list_buff[2] = str_len[2]
        list_buff[3] = str_len[3]

    def GetCmd(self, list_buff):
        str_buff = ''.join(list_buff[0:15])
        num = struct.unpack_from('!i', str_buff, 8)
        return num[0]

    def GetSubCmd(self, str_buff):
        return 0

    def BodyLen(self, list_buff):
        str_buff = ''.join(list_buff[0: 15])
        num = struct.unpack_from('!i', str_buff, 0)
        return num[0]

    def GetCheckCode(self, list_buff):
        str_buff = ''.join(list_buff[0:15])
        num = struct.unpack_from('!B',list_buff, 14)
        return num[0]

    def WriteCheckCode(self, list_buff, check_code):
        list_buff[14] = chr(check_code)

class JDHead(INetHead) :
    def __init__(self):
        INetHead.__init__(self)
        self.length = 0                 # 0-3 packge len, including self 4 bytes
        self.magic_word = ''            # 4-5  JD

    @classmethod
    def HeadLen(cls):
        return  6

    def CheckHead(self, list_buf):
        if('J' == list_buf[4]  and 'D' == list_buf[5]):
            return True
        else:
            return False

    def ParsePacketLen(self, list_buf):
        return self.BodyLen(list_buf)

    def WriteHead(self, list_buff):
        list_buff += list(struct.pack("!I", (self.HeadLen()&0xFFFFFFFF)))
        list_buff += list('J')
        list_buff += list('D')

    def WritePacketLen(self, list_buff):
        nLen = len(list_buff)
        str_len = list(struct.pack("!i", nLen))
        list_buff[0] = str_len[0]
        list_buff[1] = str_len[1]
        list_buff[2] = str_len[2]
        list_buff[3] = str_len[3]

    def BodyLen(self, list_buff):
        str_buff = ''.join(list_buff[0:5])
        num = struct.unpack_from('!i', str_buff, 0)
        return num[0]

    def GetCheckCode(self, list_buff):
        return 0

    def WriteCheckCode(self, list_buff, check_code):
        pass


class ProtocolParser:

    m_protocol = g_proctol

    @classmethod
    def SetParseProtocol(cls, pro):
        cls.m_protocol = pro

    @classmethod
    def ParseProtocol(cls):
        return  cls.m_protocol

    @staticmethod
    def GetHeadObj(protocol_type):
        if (const.BY9_PROTOCOL == protocol_type):
            return  BY9Head()
        elif (const.CHESS_PROTOCOL == protocol_type):
            return  ChessHead()
        elif (const.QEV1_PROTOCOL == protocol_type):
            return  QEV1Head()
        elif (const.QE_PROTOCOL == protocol_type):
            return  QEHead()
        elif (const.JD_PROTOCOL == protocol_type):
            return  JDHead()
        else:
            return  BY9Head()

    @staticmethod
    def ParseHeadLen(protocol_type):
        if (const.BY9_PROTOCOL == protocol_type):
            return  BY9Head.HeadLen()
        elif (const.CHESS_PROTOCOL == protocol_type):
            return  ChessHead.HeadLen()
        elif (const.QEV1_PROTOCOL == protocol_type):
            return  QEV1Head.HeadLen()
        elif (const.QE_PROTOCOL == protocol_type):
            return  QEHead.HeadLen()
        elif (const.JD_PROTOCOL == protocol_type):
            return  JDHead.HeadLen()
        else:
            return  BY9Head.HeadLen()






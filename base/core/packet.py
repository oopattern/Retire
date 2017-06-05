#packet.py
# -*- coding: utf-8 -*-

import sys, os, struct
from  protocol import *
from const import *
from  log import *

const.BY_MAX_PACKET_LEN = 1024*31

class BasePacket :
    def __init__(self):
        self.Reset()

    def __del__(self):
        del self.list_buff

    def Reset(self):
        self.list_buff = []
        self.m_pos = 0
        self.m_protocol = ProtocolParser.ParseProtocol()
        self.m_bIsEncrypted = False

    def PacketStrBuf(self):
        return ''.join(self.list_buff)

    def PacketListBuf(self):
        return self.list_buff

    def PacketSize(self):
        return len(self.list_buff)

    def CopyFromListBuf(self, list_buf):
        self.Reset()
        if(len(list_buf) > const.BY_MAX_PACKET_LEN):
            return  False
        else:
            self.list_buff = list_buf
            self.m_protocol = ProtocolParser.ParseProtocol()
            headLen = ProtocolParser.ParseHeadLen(self.m_protocol)
            self.m_pos = headLen

    def CopyFromStrBuf(self, str_buf):
        self.Reset()
        if(len(str_buf) > 1024*31):
            return  False
        else:
            self.list_buff = list(str_buf)
            self.m_protocol = ProtocolParser.ParseProtocol(self.list_buff)
            headLen = ProtocolParser.ParseHeadLen(self.m_protocol)
            self.m_pos = headLen

    def HeadLength(self):
        return ProtocolParser.ParseHeadLen(self.m_protocol)

    def BodyLength(self):
        return 0

    def WriteCheckCode(self, nValue):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        head.WriteCheckCode(self.list_buff, nValue)
        return 0

    def GetCheckCode(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        check_code = head.GetCheckCode(self.list_buff)
        return check_code

    def GetCmd(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        cmd = head.GetCmd(self.list_buff)
        return cmd

    def GetMsgType(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        msg_type = head.GetMsgType(self.list_buff)
        return msg_type

    def GetSubCmd(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        cmd = head.GetSubCmd(self.list_buff)
        return cmd

    def GetVersion(self):
        return 0


class InputPacket ( BasePacket):
    def __init__(self):
        BasePacket.__init__(self)

    def __del__(self):
        pass

    def ReadInt32(self):
        if((self.m_pos + 4)  > len(self.list_buff)):
            return 0
        else:
            #num = struct.unpack_from('!i', self.list_buff, self.m_pos)
            str = ''.join(self.list_buff[self.m_pos:self.m_pos+4])
            num = struct.unpack('!i', str)
            self.m_pos += 4
            return  num[0]

    def ReadInt64(self):
        if((self.m_pos + 8)  > len(self.list_buff)):
            return 0
        else:
            #num = struct.unpack_from('!q', self.list_buff, self.m_pos)
            str = ''.join(self.list_buff[self.m_pos:self.m_pos+8])
            num = struct.unpack('!q', str)
            self.m_pos += 8
            return  num[0]

    def ReadShort(self):
        if((self.m_pos + 2)  > len(self.list_buff)):
            return 0
        else:
            #num = struct.unpack_from('!H', self.list_buff, self.m_pos)
            str = ''.join(self.list_buff[self.m_pos:self.m_pos+2])
            num = struct.unpack('!H', str)
            self.m_pos += 2
            return  num[0]

    def ReadByte(self):
        if((self.m_pos + 1)  > len(self.list_buff)):
            return 0
        else:
            #num = struct.unpack_from('!B', self.list_buff, self.m_pos)
            str = self.list_buff[self.m_pos]
            num = struct.unpack('!B', str)
            self.m_pos += 1
            return  num[0]

    def ReadString(self):
        nLen = self.ReadInt32()
        bufLen = len(self.list_buff)

        if(0 == nLen):
            return ''
        else:
            str = ''
            if((self.m_pos + nLen) > bufLen):
                str = ''.join(self.list_buff[self.m_pos:])
                self.m_pos += (bufLen - self.m_pos)
            else:
                str = ''.join(self.list_buff[self.m_pos: self.m_pos+nLen])
                self.m_pos += nLen
            return  str

    def ReadBinary(self):
        nLen = self.ReadInt32()
        bufLen = len(self.list_buff)
        if(0 == nLen):
            return ''
        else:
            str = ''
            if((self.m_pos + nLen) > bufLen):
                str = ''.join(self.list_buff[self.m_pos:])
                self.m_pos += (bufLen - self.m_pos)
            else:
                str = ''.join(self.list_buff[self.m_pos: self.m_pos+nLen])
                self.m_pos += nLen
            return  str

class OutPacket ( BasePacket):
    def __init__(self):
        BasePacket.__init__(self)

    def __del__(self):
        pass

    def Begin(self, cmd, cversion = 0x1):
        self.m_protocol = ProtocolParser.ParseProtocol()
        head = ProtocolParser.GetHeadObj(self.m_protocol)      
        head.WriteHead(self.list_buff, cmd, cversion)

    def End(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        head.WritePacketLen(self.list_buff)

    def WriteInt32(self, intValue):
        intbytes = struct.pack("!i",  (intValue&0xFFFFFFFF))
        self.list_buff += list(intbytes)


    def WriteInt64(self, int64Value):
        int64bytes = struct.pack("!q",  int64Value)
        self.list_buff += list(int64bytes)

    def WriteShort(self, shortValue):
        shortBytes = struct.pack("!H", (shortValue&0xFFFF))
        self.list_buff += list(shortBytes)


    def WriteByte(self, byte):
        ch = struct.pack("!B", (byte&0xFF))
        self.list_buff += list(ch)

    def WriteString(self, str):
        str_len = len(str)
        if 0 == str_len:
            self.WriteInt32(1)
            self.list_buff += list('\000')
        else:
            if('\000' == str[-1]):
                self.WriteInt32(str_len)
                self.list_buff += list(str)
            else:
                self.WriteInt32(str_len+1)
                self.list_buff += list(str)
                self.list_buff += list('\000')

    def WriteBinary(self, raw_data):
        raw_len = len(raw_data)
        self.WriteInt32(raw_len)
        if(raw_len > 0):
            self.list_buff += list(raw_data)

class JdBasePacket():

    def __init__(self):
        self.Reset()

    def __del__(self):
        del self.list_buff

    def Reset(self):
        self.list_buff = []
        self.m_protocol = ProtocolParser.ParseProtocol()

    def PacketStrBuf(self):
        return ''.join(self.list_buff)

    def PacketListBuf(self):
        return self.list_buff

    def PacketSize(self):
        return len(self.list_buff)

    def HeadLength(self):
        return ProtocolParser.ParseHeadLen(self.m_protocol)

    def GetCmd(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        cmd = head.GetCmd(self.list_buff)
        return cmd

    def GetMsgType(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        msg_type = head.GetMsgType(self.list_buff)
        return msg_type

class JDInput(JdBasePacket):
    def __init__(self):
        JdBasePacket.__init__(self)

    def __del__(self):
        pass

    def ReadInt32(self):
        if((self.m_pos + 4)  > len(self.list_buff)):
            return 0
        else:
            #num = struct.unpack_from('!i', self.list_buff, self.m_pos)
            str = ''.join(self.list_buff[self.m_pos:self.m_pos+4])
            num = struct.unpack('!i', str)
            self.m_pos += 4
            return  num[0]

    def ReadBinary(self):
        nLen = self.ReadInt32()
        bufLen = len(self.list_buff)
        if(0 == nLen):
            return ''
        else:
            str = ''
            if((self.m_pos + nLen) > bufLen):
                str = ''.join(self.list_buff[self.m_pos:])
                self.m_pos += (bufLen - self.m_pos)
            else:
                str = ''.join(self.list_buff[self.m_pos: self.m_pos+nLen])
                self.m_pos += nLen
            return  str


class JDOutput( JdBasePacket):
    def __init__(self):
        JdBasePacket.__init__(self)

    def __del__(self):
        pass

    def Begin(self):
        self.m_protocol = ProtocolParser.ParseProtocol()
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        head.WriteHead(self.list_buff)

    def End(self):
        head = ProtocolParser.GetHeadObj(self.m_protocol)
        head.WritePacketLen(self.list_buff)

    def WriteInt32(self, intValue):
        intbytes = struct.pack("!i",  (intValue&0xFFFFFFFF))
        self.list_buff += list(intbytes)

    def WriteBinary(self, raw_data):
        raw_len = len(raw_data)
        self.WriteInt32(raw_len)
        if(raw_len > 0):
            self.list_buff += list(raw_data)



class CPacketParser:
    def __init__(self):
        self.m_proctol = 0
        pass

    def __del__(self):
        pass

    def ParsePacket(self, list_buf):
        buf_len = len(list_buf)
        proctol = ProtocolParser.ParseProtocol()
        self.m_proctol = proctol
        head_len = ProtocolParser.ParseHeadLen(proctol)
        head_obj = ProtocolParser.GetHeadObj(proctol)

        if((buf_len < 6) or (buf_len<head_len)):
            return  0

        return buf_len

        # lidi lidi lidi
#         if(not head_obj.CheckHead(list_buf)):
#             return  -1

        # lidi lidi lidi 
#         packet_len = head_obj.ParsePacketLen(list_buf)
#         if(packet_len<=0 or packet_len>= const.BY_MAX_PACKET_LEN):
#             return -1
#         elif buf_len < packet_len:
#             return 0
#         else:
#             return  packet_len
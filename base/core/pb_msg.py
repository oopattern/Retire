# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：pb_msg.py
# 日期：2017/2/14-17:32
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
from log import *
class PbMessage:
    def __init__(self, pb_msg_):
        self.pb_msg = pb_msg_

    def __del__(self):
        self.pb_msg = None

    def __GetMessageType(self):
        return self.pb_msg

    def New(self):
        msg = PbMessage(self.pb_msg)
        return msg

    def Encode(self):
        str_buf = self.pb_msg.SerializeToString()
        return str_buf

    def Decode(self, str_buf):
        self.pb_msg.ParseFromString(str_buf)
        return True
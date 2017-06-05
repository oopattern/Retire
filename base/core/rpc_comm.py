# -*- coding: utf-8 -*
#--------------------------------------------------
# 程序：
# 作者：ColeCai-蔡君君
# 文件：rpc_comm.py
# 日期：2017/2/13-12:05
# 版本：1.0.0
# 环境：python 2.7
# 组件：
# 描述：
# 备注：
#--------------------------------------------------
from const import *

const.RPC_JD_MSGTYPE = 0x05
#const.MsgType_Business                = 0x1
#const.MsgType_Manage                  = 0x2
#const.MsgType_Broadcast               = 0x3
#const.MsgType_Multicast               = 0x4
const.RPC_CMD = 0x1001

const.RPC_TYPE_REQUEST = 1
const.RPC_TYPE_RESPONSE = 2
const.PRC_TYPE_CTRL = 3
const.RPC_TYPE_MYSQL = 4

const.MYSQL_OP_INSERT = 0
const.MYSQL_OP_DELETE = 1
const.MYSQL_OP_UPDATE = 2
const.MYSQL_OP_SELECT = 3

const.SRPC_SUCCESS = 0
const.SRPC_ERR_SYSTEM_ERROR = -1  # 系统错误,默认未知错误
const.SRPC_ERR_PARA_ERROR = -2  # 创建req/resp参数同一组发送错误
const.SRPC_ERR_INVALID_PKG = -3  # 无效的包
const.SRPC_ERR_INVALID_PKG_HEAD = -4  # 无效的rpc包头
const.SRPC_ERR_INVALID_PKG_BODY = -5  # 无效的rpc包体
const.SRPC_ERR_INVALID_METHOD_NAME = -6  # 无效的方法名
const.SRPC_ERR_HEADER_UNINIT = -7  # rpc包头未正确初始化
const.SRPC_ERR_BODY_UNINIT = -8  # rpc包体未正确初始化
const.SRPC_ERR_NO_MEMORY = -9  # 内存不够
const.SRPC_ERR_TIMEOUT = -10  # 超时
const.SRPC_ERR_NETWORK = -11  # 网络错误
const.SRPC_ERR_RECV_TIMEOUT = -12  # 接收超时
const.SRPC_ERR_SEND_RECV_FAILED = -13  # 发送失败
const.SRPC_ERR_INVALID_ENDPOINT = -14
const.SRPC_ERR_GET_ROUTE_FAILED = -15  # 获取路由失败
const.SRPC_ERR_INVALID_SEQUENCE = -16  # 无效的序列号
const.SRPC_ERR_NO_BODY = -17  # rpc没有包体
const.SRPC_ERR_SERVICE_IMPL_FAILED = -18  # 实现错误
const.SRPC_ERR_BACKEND = -19
const.SRPC_ERR_FRAME_MAX = -99  # rpc 框架错误,最大值


const.MYSQL_SERVICE = "MySQLService.MySQL"

global seq
seq = 0


def newseq():
    global seq
    seq += 1
    if seq > 0x7fffffee:
        seq = 1
    return seq

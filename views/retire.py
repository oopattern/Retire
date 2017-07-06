# -*- coding: utf-8 -*-
import os
import sys
import json
sys.path.append('models/socket')
sys.path.append('models/protocol') 
from bysocket import BYSocket
from packet import OutPacket
from flask import Flask,request,render_template
from views import app

"""
if (platform.system() != "Windows"):
    import redis
"""

OPTION_RETIRE_KEY = "sys_key_retire_alloc" # 退休操作码校验
OPTION_EXIT_KEY = "sys_key_exit_game" # 退出进程操作码校验
CMD_GET_SERVER_INFO = 0x0906 # 内部命令，获取gameserver信息(等级，sid，玩家人数等)
CMD_SET_SERVER_RETIRED_WEB = 0x0907 # 内部命令(web控制后台使用)，将系统retire
CMD_REQUEST_EXIT_SERVER = 0x908 # 内部命令(web控制后台使用)，通知Alloc退出Game进程

# redis配置
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6333
REDIS_KEY_TURNMONEY = "TurnMoneyRecode" # 输赢排行榜key
REDIS_KEY_ALLMONEY = "AllMoneyRecode" # 资产排行榜key
g_redisConn = None


# 普通场Alloc配置
threeland = [("192.168.201.75",6580), # Level60
             ("192.168.201.75",6581), # Level61
             ("192.168.201.75",6582), # Level62
             ("192.168.201.75",6583), # Level63
             ("192.168.201.75",6584), # Level64
             ]
# 癞子场Alloc配置
laiziland = [("192.168.201.75",6585), # Level2501
             ("192.168.201.75",6586), # Level2502
             ("192.168.201.75",6587), # Level2503
             ]
# 双癞子场Alloc配置
doublelaizi = [("192.168.201.75",6560), # Level5001
               ("192.168.201.75",6561), # Level5002
               ("192.168.201.75",6562), # Level5003
               ("192.168.201.75",6563), # Level5004
             ]
# 四人场Alloc配置
fourland = [("192.168.201.75",6522), # Level1001
            ("192.168.201.75",6523), # Level1002
            ("192.168.201.75",6524), # Level1003
             ]

# 不同场次请求Alloc不同的端口
allLevel = {u'普通场': threeland,
            u'癞子场': laiziland,
            u'双癞子场': doublelaizi,
            u'四人场': fourland}

# 展示退休页面
@app.route('/retire', methods=['GET'])
def ShowRetire(choice=u'普通场', htmlLog=''):
    op = GetServerInfo(allLevel[choice])
    return render_template('retire.html', title=choice, changci=json.dumps(op)) + htmlLog
    #     return json.dumps(op)
    
# 执行退休操作
def OperateRetire(op):
    ret = SetRetireServer(op)
    return ret
    
# 处理退休表单请求
@app.route('/retire', methods=['POST'])
def HandleRetire():
    allop = request.form['opform'] # form is dict data type, key: opform, value is unicode
    op = json.loads(allop) # unicode to dict
    # 根据html选择的场次分别展示
    if('levelswitch' in op):
        print(op)
        return ShowRetire(op['levelswitch'])
    # 退休操作
    elif('retiremenu' in op):
        print(op)
        ret = OperateRetire(op)
        if ret == 1:
            tip = u'<p>操作成功</p>'
        elif ret == 0:
            tip = u'<p>无操作</p>'
        else:
            tip = u'<p>操作失败，不能2组同时退休</p>'
        htmlLog = json.dumps(op) + tip
        # 重新展示页面
        return ShowRetire(op['retiremenu'], htmlLog)
#         return json.dumps(op) # dict to json string
    # 关闭进程
    elif('exitmenu' in op):
        print(op)
        ret = RequestExitServer(op)
        if ret == 1:
            tip = u'<p>操作成功</p>'
        elif ret == 0:
            tip = u'<p>无操作</p>'
        else:
            tip = u'<p>操作失败，未退休或者玩家人数过多</p>'
        htmlLog = json.dumps(op) + tip
        # 重新展示页面
        return ShowRetire(op['exitmenu'], htmlLog)
    return 'command not found'

# 请求Alloc退出进程
def RequestExitServer(op):
    result = 0 # 0:none, 1:success, -1:failed
    leveltbl = op['level']
    group = int(op['group'])
    for item in allLevel[op['exitmenu']]:
        # 组包 - 协议和alloc对应
        outPkg = OutPacket()
        outPkg.Begin(CMD_REQUEST_EXIT_SERVER)
        outPkg.WriteString(OPTION_EXIT_KEY)
        outPkg.WriteInt32(group)
        outPkg.WriteInt32(len(leveltbl))
        for var in leveltbl:
            outPkg.WriteInt32(var)
        outPkg.End()
        # 发包 &收包
        s = BYSocket()
        s.CreatSock(item)
        inPkg = s.RequestData(outPkg)
        # 解包
        if inPkg == None:
            print("SetRetireServer no response")
        elif(inPkg.GetCmd() == CMD_REQUEST_EXIT_SERVER):
            ret = inPkg.ReadInt32() # read short -1 turn to 65535, so use int
            # 其中一个执行失败也返回失败
            if ret < 0:
                return -1
            # 无操作
            elif ret == 0:
                continue
            # 其中一个执行成功
            elif ret == 1:
                result = 1
    return result

# 请求Alloc执行退休
def SetRetireServer(op):
    result = 0 # 0:none, 1:success, -1:failed
    leveltbl = op['level']
    action = int(op['action'])
    group = int(op['group'])
    for item in allLevel[op['retiremenu']]:
        # 组包 - 协议和alloc对应
        outPkg = OutPacket()
        outPkg.Begin(CMD_SET_SERVER_RETIRED_WEB)
        outPkg.WriteString(OPTION_RETIRE_KEY)
        outPkg.WriteShort(action)
        outPkg.WriteInt32(group)
        outPkg.WriteInt32(len(leveltbl))
        for var in leveltbl:
            outPkg.WriteInt32(var)
        outPkg.End()
        # 发包 &收包
        s = BYSocket()
        s.CreatSock(item)
        inPkg = s.RequestData(outPkg)
        # 解包
        if inPkg == None:
            print("SetRetireServer no response")
        elif(inPkg.GetCmd() == CMD_SET_SERVER_RETIRED_WEB):
            ret = inPkg.ReadInt32() # read short -1 turn to 65535, so use int
            # 其中一个退休失败也返回失败
            if ret < 0:
                return -1
            # 无操作
            elif ret == 0:
                continue
            # 其中一个执行成功
            elif ret == 1:
                result = 1
    return result

# 请求Alloc获取场次信息
def GetServerInfo(addrTbl):
    msg = [] # all level and all group
    uniLevel = [] # unique level
    # 每个Level发送一个alloc命令
    for item in addrTbl:
        # 组包 - 协议和alloc对应
        outPkg = OutPacket()
        outPkg.Begin(CMD_GET_SERVER_INFO)
        outPkg.End()
        # 发包 &收包
        s = BYSocket()
        s.CreatSock(item)
        inPkg = s.RequestData(outPkg)
        # 解包
        if inPkg == None:
            print("GetServerInfo no response")
        elif(inPkg.GetCmd() == CMD_GET_SERVER_INFO):
            num = inPkg.ReadInt32()
            for var in range(num):
                grpidx = inPkg.ReadInt32()
                level = inPkg.ReadInt32()
                usercount = inPkg.ReadInt32()
                gameip = inPkg.ReadString()
                gameport = inPkg.ReadInt32()
                retirestat = inPkg.ReadInt32()
                starttime = inPkg.ReadInt32() # 获取进程启动时间，根据最小启动时间判断程序是否更新完毕
                gameip = gameip[:gameip.index('\x00')] # 删除空白字符 \u000
                # 和html的字段格式相匹配
                uniLevel.append(level)
                msg.append({"host":gameip, "level":level, "group"+str(grpidx):{"usercount":usercount,"stat":retirestat,"starttime":starttime}})        
                # print 'cmd[%s] level[%s] usercount[%s] gameip[%s] gameport[%s] retire_stat[%s]' % (cmd,level,usercount,gameip,gameport,retirestat)
    msg.append({'host': '192.168.201.75', 'level': 60, 'group1': {"usercount":24,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 60, 'group2': {"usercount":33,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 60, 'group2': {"usercount":17,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 61, 'group1': {"usercount":135,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 61, 'group2': {"usercount":48,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 61, 'group2': {"usercount":31,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 62, 'group1': {"usercount":23,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 62, 'group2': {"usercount":129,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 2501, 'group1': {"usercount":346,"stat":0,"starttime":sys.maxint}})
    msg.append({'host': '192.168.201.75', 'level': 5001, 'group2': {"usercount":478,"stat":0,"starttime":sys.maxint}})
    # 校验1：同一个group的退休状态必须相同
    # 校验2：同一个level必须有Group1和Group2
    # 根据level和group index合并计算usercount的数目
#     for item in msg:
#         print item
    show = []
    uniLevel = list(set(uniLevel))
    for level in uniLevel:
        tmp = {}
        for item in msg:
            if level == item['level']:
                if tmp == {}:
                    tmp = {"host":item['host'], 
                           "level":item['level'],
                           "starttime":sys.maxint,
                           "group1":{"usercount":0,"stat":-1,"starttime":sys.maxint}, 
                           "group2":{"usercount":0,"stat":-1,"starttime":sys.maxint}}
                # 初始化group1
                if item.has_key('group1'):
                    # 退休状态 
                    if tmp['group1']['stat'] == -1: 
                        tmp['group1']['stat'] = item['group1']['stat']
                    # 计算玩家人数
                    tmp['group1']['usercount'] += item['group1']['usercount']
                    # 进程最小启动时间
                    if item['group1']['starttime'] < tmp['group1']['starttime']:
                        tmp['group1']['starttime'] = item['group1']['starttime']
                # 初始化group2
                if item.has_key('group2'):
                    # 退休状态 
                    if tmp['group2']['stat'] == -1:
                        tmp['group2']['stat'] = item['group2']['stat']
                    # 计算玩家人数
                    tmp['group2']['usercount'] += item['group2']['usercount']
                    # 进程最小启动时间
                    if item['group2']['starttime'] < tmp['group2']['starttime']:
                        tmp['group2']['starttime'] = item['group2']['starttime']
        show.append(tmp)
    # sort by level
    show = sorted(show, cmp=lambda x,y : cmp(x['level'], y['level'])) 
    for item in show:
        print item
    # 重新构造显示的html内容
    return show



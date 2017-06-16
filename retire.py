# -*- coding: utf-8 -*-    
import os
import sys
import json
sys.path.append('base/socket')
sys.path.append('base/protocol')
from bysocket import BYSocket
from packet import OutPacket
from flask import Flask,request,render_template

# 内部命令，获取gameserver信息(等级，sid，玩家人数等)
CMD_GET_SERVER_INFO = 0x0906

app = Flask(__name__)

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

# 展示退休页面
@app.route('/retire', methods=['GET'])
def ShowRetire(choice=u'普通场'):
    # 不同场次请求Alloc不同的端口
    allLevel = {u'普通场': threeland,
                u'癞子场': laiziland,
                u'双癞子场': doublelaizi,
                u'四人场': fourland}
    op = GetServerInfo(allLevel[choice])
    return render_template('retire.html', title=choice, changci=json.dumps(op))
    
# 处理退休表单请求
@app.route('/retire', methods=['POST'])
def HandleRetire():
    allop = request.form['opform'] # form is dict data type, key: opform, value is unicode
    op = json.loads(allop) # unicode to dict
    # 根据html选择的场次分别展示
    if('levelswitch' in op):
        return ShowRetire(op['levelswitch'])
    return json.dumps(op) # dict to json string

# 请求Alloc获取场次信息
def GetServerInfo(addrTbl):
    msg = []
    for item in addrTbl:
        # 组包
        outPkg = OutPacket()
        outPkg.Begin(CMD_GET_SERVER_INFO)
        outPkg.End()
        # 发包 & 收包
        s = BYSocket()
        s.CreatSock(item)
        inPkg = s.RequestData(outPkg)
        # 解包
        cmd = hex(inPkg.GetCmd())
        level = inPkg.ReadInt32()
        usercount = inPkg.ReadInt32()
        gameip = inPkg.ReadString()
        gameport = inPkg.ReadInt32()
        retirestat = inPkg.ReadInt32()
        gameip = gameip[:gameip.index('\x00')] # 删除空白字符 \u000
        # 和html的字段格式相匹配
        msg.append({"host":gameip, "level":level, "playnum":usercount})
        # print 'cmd[%s] level[%s] usercount[%s] gameip[%s] gameport[%s] retire_stat[%s]' % (cmd,level,usercount,gameip,gameport,retirestat)
    return msg

    
if __name__ =='__main__':
    print('say goodbye!')
    app.run(host='localhost', port=8088)
    
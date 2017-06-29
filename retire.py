# -*- coding: utf-8 -*-    
import os
import sys
import json
import platform
sys.path.append('base/socket')
sys.path.append('base/protocol')
from bysocket import BYSocket
from packet import OutPacket
from flask import Flask,request,render_template

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

# 展示图表页面
@app.route('/chart', methods=['GET'])
def ShowChart():    
    return render_template('chart.html')

# 展示大数据页面
@app.route('/spark', methods=['GET'])
def ShowSpark():
    turnMoney,allMoney = GetWinLoseRank()
#     return '输赢排行榜xx:' + '<br/>' + turnMoney + '<br/>' + '资产排行榜yy:' + '<br/>' + allMoney
    return render_template('spark.html', turnmoney=turnMoney, allmoney=allMoney)

# 读取排行榜信息
def GetWinLoseRank():
    """
    # 从redis读取输赢排行榜和资产排行榜信息
    if (platform.system() != "Windows"):
        if(g_redisConn == None):
            print('init redis client')
            g_redisConn = redis.Redis(REDIS_HOST, REDIS_PORT)
        turnMoneyRank = g_redisConn.get(REDIS_KEY_TURNMONEY)
        allMoneyRank = g_redisConn.get(REDIS_KEY_ALLMONEY)
    else:
    """
    turnMoneyRank = "[[2562393, 99209900000], [2858301, 29879626041], [1564526, 24182134358], [3140684, 12918700000], [1886791, 9307921743], [2208462, 9077411363], [3154947, 8602867386], [2226618, 7828288435], [3072474, 7821858249], [3159805, 7633058618], [2216159, 7595876572], [2292512, 7579307559], [1736720, 7217173115], [2834782, 7178993386], [1613032, 7122169595], [2256362, 7082006899], [2856642, 7059509008], [1977076, 6692928793], [2627495, 6575477682], [348221, 6536200000], [1809372, 6375131115], [2031187, 6337153846], [3010635, 6310808035], [3022774, 6163909758], [2678032, 6147950831], [2487017, 6124200000], [3124154, 6073464297], [3053601, 6017019986], [1795823, 5971952010], [2918261, 5849308421], [3041375, 5810545200], [303306, 5647478071], [3132685, 5607716618], [1977635, 5574520409], [2351673, 5565753695], [2238727, 5565056588], [2938145, 5478339098], [400700, 5438697416], [2926174, 5372919046], [2681861, 5308516197], [248686, 5134078919], [515693, 4844900544], [2460355, 4679903240], [2431289, 4571457024], [285288, 4270919381], [228564, 4270500000], [2108603, 4167847102], [145038, 3930276069], [2638386, 3889677179], [841398, 3885182962], [2922532, 3710992000], [2719258, 3571451717], [2523932, 3563435484], [2148812, 3537500000], [2063182, 3507586914], [2870228, 3499062946], [487112, 3455298172], [901577, 3441989195], [2461088, 3425452523], [1522958, 3405272908], [2244152, 3387805343], [432826, 3360055583], [2589692, 3292897539], [693210, 3289222763], [1797588, 3245647734], [3150711, 3190433834], [2319763, 3090240686], [2792208, 3081000000], [2644437, 3075368886], [2261742, 3057384624], [1319851, 2983900000], [2221500, 2954470979], [1947358, 2896792827], [2797642, 2887296777], [2439357, 2815222833], [261848, 2789262077], [1922557, 2784500000], [2973719, 2747024823], [2296253, 2731079332], [659987, 2726503653], [3162309, 2710971181], [2943963, 2708458048], [3156190, 2657793010], [3063146, 2629094156], [3096633, 2624227672], [100319, 2602240000], [3153865, 2601391239], [3087551, 2579329455], [2651734, 2538611952], [1809603, 2537757268], [1887017, 2530690993], [1249405, 2498879109], [3160936, 2497629611], [3108334, 2464352895], [3145919, 2431583429], [2066211, 2431000000], [1592401, 2390621282], [2033122, 2388204818], [337507, 2373893785], [2273362, 2367319905]]"
    allMoneyRank = "[[2562393, 400130313237], [364736, 104270955008], [2781697, 100682414371], [1396119, 94350680723], [2858301, 82901043249], [2292790, 74696605049], [1564526, 72600486380], [705690, 66724740082], [1338092, 55350702944], [2462214, 52193057924], [2460379, 47499285610], [487112, 37455373963], [1493287, 37246271352], [771061, 36635945031], [2938145, 36343476667], [1988903, 34975701532], [1004711, 33729171761], [1076970, 33045058605], [2678032, 29015759624], [1465553, 27979254498], [854590, 26976454301], [2238727, 26204026432], [2780624, 25324546607], [205162, 24265085375], [492993, 24223765419], [463865, 23530630832], [1988542, 23150851149], [2108603, 22697980834], [849396, 22515428684], [872459, 22000031833], [235187, 21906325487], [2319763, 21721856108], [1343445, 21206904101], [1886791, 21067255701], [2606030, 20283171173], [2866569, 20086198742], [2351673, 20002880130], [1707487, 19605537517], [1056645, 19576259816], [2037579, 19293295424], [632482, 18546587996], [3140684, 18327500000], [2167260, 18221610309], [2512772, 18076770779], [2777488, 17936794884], [1337890, 17617539751], [3124154, 17441686458], [681439, 17240425053], [2669616, 16875110252], [1257874, 16574148518], [248686, 16290686141], [1221949, 16061346394], [1795823, 15928944336], [2943963, 15805842522], [348221, 15795424600], [528408, 15709938754], [2837618, 15578170059], [2489024, 14817136414], [289857, 14735999556], [1809372, 14633000565], [409785, 14574035799], [169385, 14360156659], [421935, 14181779512], [1435808, 14092821691], [515693, 14015819454], [1420453, 13998589915], [2487017, 13878616573], [2661460, 13801158440], [2216159, 13688311552], [419305, 13539164587], [1574585, 13505864675], [2380860, 13502297841], [813213, 13032172599], [2524716, 12849863539], [702464, 12652150788], [2523932, 12609958417], [608495, 12585858489], [2431289, 12528031051], [2978709, 12426865398], [1568042, 12273735651], [3053601, 12162130876], [1268945, 12138892174], [1974783, 12027515315], [662797, 12015059456], [1135158, 11992709228], [1418898, 11641322856], [486041, 11600469759], [672764, 11567745720], [2183273, 11553023820], [2214072, 11423041779], [2034544, 11343965662], [1677582, 11296309914], [1140935, 11282870958], [1191365, 11211711362], [2031187, 11204618488], [2208462, 11094590087], [1807222, 11018891801], [108395, 10908315954], [2651291, 10767671201], [247615, 10747254474]]"
#     turnMoneyList = json.loads(turnMoneyRank)
#     allMoneyList = json.loads(allMoneyRank)
    # 提供给前端展示
    return turnMoneyRank,allMoneyRank

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

# 守护进程
def Daemonize():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # first parent out
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    #os.chdir("/")
    #os.umask(0)
    os.setsid()

    for f in sys.stdout, sys.stderr:
        f.flush()
    si = file('/dev/null', 'r')
    so = file('/dev/null', 'w')
    se = file('/dev/null', 'w')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

if __name__ =='__main__':
    print('say goodbye!')
    if (platform.system() != "Windows"):
        Daemonize()
        print('run web server')
        # threaded=True支持多个用户同时请求
        app.run(host='192.168.201.94', port=9999, threaded=True)
    else:
        print('run web server')
        # threaded=True支持多个用户同时请求
        app.run(host='localhost', port=9999, threaded=True)

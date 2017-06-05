# -*- coding: utf-8 -*-    
import os
import sys
import time
import json
import socket
from multiprocessing import Process
from flask import Flask,request,render_template
# use for own
sys.path.append("base/core")
from packet import *
from encrypt import *
from clienthandler import *
from tcpclient import *
from reactor import *
import server_unit_test

app = Flask(__name__)

# 展示退休页面
@app.route('/retire', methods=['GET'])
def ShowRetire():
    fourLevel = [{"host": "192.168.201.189", "level": 10086, "playnum": 371, "option": "None"},
                 {"host": "192.168.201.5",   "level": 20033, "playnum": 496, "option": "None"}]
    doublelaiziLevel = [{"host": "192.168.201.162", "level": 5001, "playnum": 268, "option": "None"},
                        {"host": "192.168.201.143", "level": 5002, "playnum": 367, "option": "None"},
                        {"host": "192.168.201.41",  "level": 5003, "playnum": 198, "option": "None"}];
    return render_template('retire.html', changci=json.dumps(fourLevel))
    
# 处理退休表单请求
@app.route('/retire', methods=['POST'])
def HandleRetire():
    return 'ooooo request'

def ProcessCommand(name):    
    while(1):
        print('[%s] run child process %s (%s)' % (time.asctime(), name, os.getpid()))
        sys.stdout.flush()
        time.sleep(5)
        
def UnitTestPacket():
    outPkg = OutPacket()
    outPkg.Begin(0x1122)
    outPkg.WriteInt32(0x1122)
    outPkg.WriteByte(0xCC)
    outPkg.WriteString("123")
    outPkg.WriteBinary("1234")
    outPkg.End()
    print 'outPkg.len=', len(outPkg.list_buff)
    print 'outPkg.str_buff=', ','.join(map(lambda x: hex(ord(x)), outPkg.list_buff))
    
def UnitTestClient():
    parser = CPacketParser()
    server = server_unit_test.TestServer()
    reactor = CReactor.Instance()
    reactor.SetPacketParser(parser)
    
    client = CTcpClient(reactor, server)
    client.InitConnect("192.168.201.159", 9999)
    reactor.RunEventLoop()
    
def RunWebServer(name):
    print('run web child process pid[%d]' % os.getpid())
    app.run(host='localhost', port=8088, debug=True)
    
if __name__ =='__main__':
#     UnitTestPacket()
    webSrvP = Process(target=RunWebServer, args=('Process WebServer',))
    webSrvP.start()
#     UnitTestClient()
    print('say goodbye!')
    
    
    
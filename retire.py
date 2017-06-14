# -*- coding: utf-8 -*-    
import os
import sys
import json
sys.path.append('base/')
from Socket import *
from flask import Flask,request,render_template

app = Flask(__name__)

# 展示退休页面
@app.route('/retire', methods=['GET'])
def ShowRetire(choice=u'普通场'):
    putongLevel = [{"host": "192.168.201.75",  "level": 201, "playnum": 276},
                    {"host": "192.168.201.159", "level": 202, "playnum": 389}]
    laiziLevel = [{"host": "192.168.201.138", "level": 2001, "playnum": 135},
                  {"host": "192.168.201.142", "level": 2002, "playnum": 498}]
    fourLevel = [{"host": "192.168.201.189", "level": 10086, "playnum": 371},
                 {"host": "192.168.201.5",   "level": 20033, "playnum": 496}]
    doublelaiziLevel = [{"host": "192.168.201.162", "level": 5001, "playnum": 268},
                        {"host": "192.168.201.143", "level": 5002, "playnum": 367},
                        {"host": "192.168.201.41",  "level": 5003, "playnum": 198}]
    allLevel = {u'普通场': putongLevel,
                u'癞子场': laiziLevel,
                u'双癞子场': doublelaiziLevel,
                u'四人场': fourLevel}
    return render_template('retire.html', changci=json.dumps(allLevel[choice]))
    
# 处理退休表单请求
@app.route('/retire', methods=['POST'])
def HandleRetire():
    allop = request.form['opform'] # form is dict data type, key: opform, value is unicode
    op = json.loads(allop) # unicode to dict
    if('levelswitch' in op):
        return ShowRetire(op['levelswitch'])
    return json.dumps(op) # dict to json string
    
if __name__ =='__main__':
    print('say goodbye!')
    address = ('127.0.0.1', 20000)
    
    s = Socket()
    s.CreatSock(address)
    
#     app.run(host='localhost', port=8088)
#     app.run(host='localhost', port=8088, debug=True)
    
    
    
    
    
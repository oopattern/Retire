# -*- coding: utf-8 -*-    
import os
import sys
import json
from flask import Flask,request,render_template

app = Flask(__name__)

# 展示退休页面
@app.route('/retire', methods=['GET'])
def ShowRetire(choice=u'普通场'):
    putongLevel = [{"host": "192.168.201.75",  "level": 201, "playnum": 276, "option": "None"},
                    {"host": "192.168.201.159", "level": 202, "playnum": 389, "option": "None"}]
    laiziLevel = [{"host": "192.168.201.138", "level": 2001, "playnum": 135, "option": "None"},
                  {"host": "192.168.201.142", "level": 2002, "playnum": 498, "option": "None"}]
    fourLevel = [{"host": "192.168.201.189", "level": 10086, "playnum": 371, "option": "None"},
                 {"host": "192.168.201.5",   "level": 20033, "playnum": 496, "option": "None"}]
    doublelaiziLevel = [{"host": "192.168.201.162", "level": 5001, "playnum": 268, "option": "None"},
                        {"host": "192.168.201.143", "level": 5002, "playnum": 367, "option": "None"},
                        {"host": "192.168.201.41",  "level": 5003, "playnum": 198, "option": "None"}]
    allLevel = {u'普通场': putongLevel,
                u'癞子场': laiziLevel,
                u'双癞子场': doublelaiziLevel,
                u'四人场': fourLevel}
    return render_template('retire.html', changci=json.dumps(allLevel[choice]))
    
# 处理退休表单请求
@app.route('/retire', methods=['POST'])
def HandleRetire():
    allop = request.form
    if(allop.has_key('allretire')):
        return '<p>' + u'执行全部退休' + '</p>'
    elif(allop.has_key('oneretire')):
        return '<p>' + u'退休一个场次' + '</p>'
    elif(allop.has_key('opmenu') and allop['opmenu'] != ''):
        return ShowRetire(allop['opmenu'])
    return 'submit option no found...'
    
if __name__ =='__main__':
    print('say goodbye!')
    app.run(host='localhost', port=8088, debug=True)
    
    
    
    
    
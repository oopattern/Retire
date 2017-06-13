# -*- coding: utf-8 -*-    
import os
import sys
import json
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
    allop = request.form['opform'] # dict data type, key: opform
    return allop
    return 'submit option no found...'
    
    """
    if(allop.has_key('opform')):
        return json.dumps(allop['opform'])
    return 'submit option no found...'
 """
 
    """   
    if(allop.has_key('retire')):
        return json.dumps(allop)
    elif(allop.has_key('levelswitch')):
        return ShowRetire(allop['levelswitch'])
    """

    """
    if(allop.has_key('allretire')):
        return '<p>' + u'执行全部退休' + '</p>'
    elif(allop.has_key('oneretire')):
        return '<p>' + u'退休一个场次' + '</p>'
    elif(allop.has_key('opmenu') and allop['opmenu'] != ''):
        return ShowRetire(allop['opmenu'])
    return 'submit option no found...'
    """
    
if __name__ =='__main__':
    print('say goodbye!')
    app.run(host='localhost', port=8088)
#     app.run(host='localhost', port=8088, debug=True)
    
    
    
    
    
# -*- coding: utf-8 -*-    
import os
import sys
import json
import platform
from flask import Flask,request,render_template
from views import app

# 展示图表页面
@app.route('/', methods=['GET'])
def ShowHome():
    return render_template('index.html')
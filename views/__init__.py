# -*- coding: utf-8 -*-
from flask import Flask,request,render_template

# 定义全局的app
app = Flask(__name__, template_folder='../templates', static_folder='../static')

from views import index, retire, rank

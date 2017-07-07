# -*- coding: utf-8 -*-    
import os
import sys
import platform
from views import app


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

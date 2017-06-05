# -*- coding: UTF-8 -*-
#const.py

from singleton import *

class Const(CSingleton):
    class ConstError(TypeError) : pass

    def __setattr__(self, key, value):
        # self.__dict__
        if self.__dict__.has_key(key):
            print (self.__dict__)
            raise (self.ConstError, "constant reassignment error! (%s)"%key)
        self.__dict__[key] = value
        #print self.__dict__

const = Const()
#import sys
#sys.modules[__name__] = Const()
#log.py
# -*- coding: utf-8 -*-
import os, sys
import logging,time,datetime
import logging.handlers
from singleton import *
from const import *

const.LOG_DEBUG = 7
const.LOG_INFO = 6
const.LOG_NOTICE = 5
const.LOG_WARNING = 4
const.LOG_ERROR = 3
const.LOG_CRIT = 2
const.LOG_BOOT = 1


def find_caller_name():
    return  '%s(%s)[%s]:'%(
        os.path.basename(sys._getframe(3).f_code.co_filename),
        sys._getframe(3).f_lineno,
        sys._getframe(3).f_code.co_name)


class CLog(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls, *args, **kw)
            cls._instance.log_level = const.LOG_DEBUG
            cls._instance.core_level = const.LOG_DEBUG
            logging.addLevelName(30, 'WARN')
            logging.addLevelName(50, 'CRIT')
            logging.addLevelName(60, 'BOOT')

            cls._instance.logger = logging.getLogger("default_log")
            cls._instance.logger.setLevel(logging.DEBUG)
            fmt = logging.Formatter('<%(levelname)5s>[%(asctime)s]%(message)s', datefmt='%Y%m%d-%H:%M:%S')
            fh = logging.StreamHandler()
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(fmt)
            cls._instance.logger.addHandler(fh)
        return cls._instance

    def InitLog(self, filename='server.log', log_dir='log'):
        self.filename = filename
        self.base_dir = log_dir
        self.sub_dir = time.strftime('%m%d')
        self.log_time = time.localtime()
        self.full_dir = self.base_dir + '/'+self.sub_dir

        if not os.path.exists(self.full_dir):
            try:
                os.makedirs(self.full_dir)
            except OSError,e:
                self.log_error("errno=%d, strerror=%s ", e.errno, os.strerror(e.errno))
                raise

        self.file_full_path = self.full_dir + '/' + self.filename
        self.logger = logging.getLogger(self.file_full_path)
        self.logger.setLevel(logging.DEBUG)

        logging.addLevelName(30, 'WARN')
        logging.addLevelName(50, 'CRIT')
        logging.addLevelName(60, 'BOOT')


        #fmt = logging.Formatter('<%(levelname)5s>[%(asctime)s]%(filename)s(%(lineno)d)[%(funcName)s]:%(message)s',
        #                        datefmt='%Y%m%d-%H:%M:%S')
        fmt = logging.Formatter('<%(levelname)5s>[%(asctime)s]%(message)s', datefmt='%Y%m%d-%H:%M:%S')
        fh = logging.FileHandler(self.file_full_path, 'a')
        #fh = logging.handlers.DatagramHandler  # for upd log
        fh.suffix = "%Y%m%d.log"

        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        self.logger.addHandler(fh)

    def OpenLog(self):
        if hasattr(self, 'log_time'):
            log_time = time.localtime()
            if(self.log_time.tm_mday != log_time.tm_mday or self.log_time.tm_mon != log_time.tm_mon):
                self.log_time = log_time
                self.InitLog(self.filename, self.base_dir)

    def log_debug(self, msg, *args, **kws):
        self.OpenLog()
        self.logger.debug(find_caller_name()+msg, *args, **kws)

    def log_info(self, msg, *args, **kws):
        self.OpenLog()
        self.logger.info(find_caller_name()+msg, *args, **kws)

    def log_warning(self, msg, *args, **kws):
        self.OpenLog()
        self.logger.warning(find_caller_name()+msg, *args, **kws)

    def log_error(self, msg, *args, **kws):
        self.OpenLog()
        self.logger.error(find_caller_name()+msg, *args, **kws)

    def log_boot(self, msg, *args, **kws):
        self.OpenLog()
        self.logger._log(60, find_caller_name()+msg, args, **kws)


def set_log_level(level_):
    logger = CLog()
    logger.log_level = level_ if level_ > const.LOG_WARNING else const.LOG_WARNING

def set_core_log_level(level_):
    logger = CLog()
    logger.core_level = level_ if level_ > const.LOG_WARNING else const.LOG_WARNING

def init_log(filename, file_dir="log"):
    logger = CLog()
    logger.InitLog(filename, file_dir)


def log_debug(msg, *args, **kws):
    logger = CLog()
    if logger.log_level >= const.LOG_DEBUG:
        logger.log_debug(msg, *args, **kws)

def log_info(msg, *args, **kws):
    logger = CLog()
    if logger.log_level >= const.LOG_INFO:
        logger.log_debug(msg, *args, **kws)

def log_warning(msg, *args, **kws):
    logger = CLog()
    if logger.log_level >= const.LOG_WARNING:
        logger.log_debug(msg, *args, **kws)


def log_err(msg, *args, **kws):
    logger = CLog()
    if logger.log_level >= const.LOG_ERROR:
        logger.log_error(msg, *args, **kws)

def log_boot(msg, *args, **kws):
    logger = CLog()
    if logger.log_level >= const.LOG_BOOT:
        logger.log_boot(msg, *args, **kws)


def core_debug(msg, *args, **kws):
    logger = CLog()
    if logger.core_level >= const.LOG_DEBUG:
        logger.log_debug(msg, *args, **kws)

def core_info(msg, *args, **kws):
    logger = CLog()
    if logger.core_level >= const.LOG_INFO:
        logger.log_info(msg, *args, **kws)

def core_warning(msg, *args, **kws):
    logger = CLog()
    if logger.core_level >= const.LOG_WARNING:
        logger.log_warning(msg, *args, **kws)

def core_err(msg, *args, **kws):
    logger = CLog()
    if logger.core_level >= const.LOG_ERROR:
        logger.log_error(msg, *args, **kws)

def core_boot(msg, *args, **kws):
    logger = CLog()
    if logger.core_level >= const.LOG_BOOT:
        logger.log_boot(msg, *args, **kws)



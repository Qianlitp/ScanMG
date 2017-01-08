#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pymongo import *
import threading
import time
import inspect
import ctypes
import IPy


lock = threading.Lock()
ip_index = 0
ip = IPy.IP('115.29.0.0/16')


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class Single(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.ip = ''
        self.size = address

    def run(self):
        global ip
        global ip_index
        while ip_index != self.size:
            lock.acquire(True)
            self.ip = str(ip[ip_index])
            ip_index += 1
            try:
                lock.release()
            except:
                pass
            scan = Scan(self.ip)
            scan.start()
            time.sleep(2)
            try:
                stop_thread(scan)
            except:
                pass


class Scan(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.address = address

    def run(self):
        try:
            client = MongoClient(self.address, 27017)
            if client.database_names():
                lock.acquire()
                f = open('result.txt', 'a')
                f.write(self.address + ' is available!\n')
                f.close()
                lock.release()
                print '--------------' + self.address + 'is available !!!!!!!-----------------'
        except:
            print self.address + ' is invalid!'


def main():
    global ip
    thread_list = []
    for x in xrange(20):
        temp = Single(len(ip))
        thread_list.append(temp)
    for single in thread_list:
        single.start()

if __name__ == '__main__':
    main()

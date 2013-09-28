#coding:utf8
import socket
import logging
import logging.handlers
import time
class IpSocketHandler(logging.handlers.SocketHandler):
    def __init__(self, host, port):
        logging.handlers.SocketHandler.__init__(self, host, port) 
        self.ip = socket.gethostname()
    def emit(self, record):
        try:
            record.msg += '\nip: '+self.ip
        except Exception as e:
            print "append msg with ip fails msg not a string"
            print e
        logging.handlers.SocketHandler.emit(self, record)
        

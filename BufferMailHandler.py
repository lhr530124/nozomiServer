#coding:utf8
import socket
import logging
import logging.handlers
import time
class BufferMailHandler(logging.handlers.SMTPHandler):
    def __init__(self, mailhost, fromaddr, toaddr, subject, credentials=None, secure=None):
        subject = socket.gethostname()+subject
        #2.6 python no secure
        logging.handlers.SMTPHandler.__init__(self, mailhost, fromaddr, toaddr, subject, credentials)
        self.lastSendTime = 0
    def emit(self, record):
        now = int(time.time())
        if now - self.lastSendTime > 3600:
            self.lastSendTime = now
            logging.handlers.SMTPHandler.emit(self, record)
        else:
            #距离上次发送时间不够不发送
            pass
        

#coding:utf8
import pickle
import logging
import logging.handlers
import SocketServer
import struct

from logging import Formatter
from logging.handlers import TimedRotatingFileHandler

#name pair fileHandler if not exist then create new file
allHandlers = {}

class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        #read log length
        #read log content
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    #record log to local file
    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        # record 中传来logger 名称
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        if allHandlers.get(name) == None:
            allHandlers[name] = True
            debugLogger = TimedRotatingFileHandler("allLog/%s.log"%(name), 'd', 1)
            debugLogger.setFormatter(Formatter(
            '''
            Message type:  %(levelname)s
            Location:      %(pathname)s:%(lineno)d
            Module:        %(module)s
            Function:      %(funcName)s
            Time:          %(asctime)s
            Message:
            %(message)s
            '''))
            logger.addHandler(debugLogger)
        logger.handle(record)

class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = 1

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        print host, port
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort

def main():
    logging.basicConfig(
        format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s')
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)
    fileHandler = logging.handlers.TimedRotatingFileHandler("allLog/allLog.log", "d", 1)
    rootLogger.addHandler(fileHandler)

    mysqlLogHandler = TimedRotatingFileHandler('allLog/mysqlLog.log', 'd', 1)
    mysqllogger = logging.getLogger("mysqlLogger")
    mysqllogger.addHandler(mysqlLogHandler)
    mysqllogger.setLevel(logging.INFO)
    allHandlers['mysqlLogger'] = True

    timeLoggerHandler = TimedRotatingFileHandler("allLog/nozomiAccess_2.log", 'd', 1)
    timeLogger = logging.getLogger("timeLogger")
    timeLogger.addHandler(timeLoggerHandler)
    timeLogger.setLevel(logging.INFO)
    allHandlers['timeLogger'] = True

    statlogger = logging.getLogger("STAT")
    f = TimedRotatingFileHandler('allLog/stat_2.log', 'd', 1)
    statlogger.addHandler(f)
    formatter = logging.Formatter("%(asctime)s\t%(message)s")   
    f.setFormatter(formatter)
    statlogger.setLevel(logging.INFO)
    allHandlers['STAT'] = True

    loginlogger = logging.getLogger("LOGIN")
    f = TimedRotatingFileHandler('allLog/login_2.log','d',1)
    loginlogger.addHandler(f)
    formatter = logging.Formatter("%(asctime)s\t%(message)s")
    f.setFormatter(formatter)
    loginlogger.setLevel(logging.INFO)
    allHandlers['LOGIN'] = True

    crystallogger = logging.getLogger("CRYSTAL")
    f = TimedRotatingFileHandler('allLog/crystal_stat_2.log', 'd', 1)
    crystallogger.addHandler(f)
    formatter = logging.Formatter("%(asctime)s\t%(message)s")   
    f.setFormatter(formatter)
    crystallogger.setLevel(logging.INFO)
    allHandlers['CRYSTAL'] = True

    testlogger = logging.getLogger("TEST")
    f = logging.FileHandler("allLog/test.log")
    testlogger.addHandler(f)
    formatter = logging.Formatter("%(asctime)s\t%(message)s")
    f.setFormatter(formatter)
    testlogger.setLevel(logging.INFO)
    allHandlers['TEST'] = True

    #app name __main__ 对应的log 
    debug = logging.getLogger("__main__")
    debugLogger = TimedRotatingFileHandler("allLog/nozomiError_4.log", 'd', 7)
    debugLogger.setLevel(logging.ERROR)
    debugLogger.setFormatter(Formatter(
    '''
    Message type:  %(levelname)s
    Location:      %(pathname)s:%(lineno)d
    Module:        %(module)s
    Function:      %(funcName)s
    Time:          %(asctime)s
    Message:
    %(message)s
    '''))
    debug.addHandler(debugLogger)
    allHandlers['__main__'] = True


    tcpserver = LogRecordSocketReceiver(host='0.0.0.0', port=9020)
    print('About to start TCP server...')
    tcpserver.serve_until_stopped()

if __name__ == '__main__':
    main()

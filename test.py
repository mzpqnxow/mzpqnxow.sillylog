#!/usr/bin/env python3
from sys import argv
import logging

from sillylog.log import get_logger

LOG, DEBUG, INFO, STATUS, WARN, ERROR, CRITICAL, EXCEPTION = get_logger(argv[0], None, level=logging.DEBUG, new=True)
FATAL = CRITICAL  # The exiting version of CRITICAL

# class MyFormatter(logging.Formatter):
#     width = 24
#     datefmt='%Y-%m-%d %H:%M:%S'

#     def format(self, record):
#         cpath = '%s:%s:%s' % (record.module, record.funcName, record.lineno)
#         cpath = cpath[-self.width:].ljust(self.width)
#         record.message = record.getMessage()
#         s = "%-7s %s %s : %s" % (record.levelname, self.formatTime(record, self.datefmt), cpath, record.getMessage())
#         if record.exc_info:
#             # Cache the traceback text to avoid converting it multiple times
#             # (it's constant anyway)
#             if not record.exc_text:
#                 record.exc_text = self.formatException(record.exc_info)
#         if record.exc_text:
#             if s[-1:] != "\n":
#                 s = s + "\n"
#             s = s + record.exc_text
#         #if record.stack_info:
#         #    if s[-1:] != "\n":
#         #        s = s + "\n"
#         #    s = s + self.formatStack(record.stack_info)
#         return s


def main(APPNAME):
    # log_h = MyFormatter()
    # logger = logging.getLogger("example")
    # # logger.(logFormatter)
    # log_format = '%(asctime)s'
    # log_format += ' %(levelname)5s '
    # log_format += APPNAME
    # log_format += ' %(name)8s'
    # log_format += ' %(filename)s::%(funcName)s::%(lineno)d'
    # log_format += ' %(message)s'
    # from logging import StreamHandler
    # log_handler = ExitingStreamHandler()

    # log_handler.setFormatter(LevelBasedFormatter(log_format, datefmt='%Y-%m-%d@%H:%M.%S'))
    # # log_handler.setFormatter(LevelBasedFormatter(log_format, datefmt='%Y-%m-%d@%H:%M.%S'))
    # logger.addHandler(log_handler)
    # addLoggingLevel('USER', logging.DEBUG - 5)
    # logger.setLevel(logging.USER)

    # # logger.setLevel(logging.NOTSET)
    # # logger.setLevel(logging.USER)
    # INFO = logger.info
    # DEBUG = logger.debug
    # WARN = logger.warning
    # ERROR = logger.error
    # CRITICAL = logger.fatal
    # USER = logger.user

    INFO('This is an informational message')
    DEBUG('This is a debug message')
    WARN('This is a warning message')
    ERROR('This is an error message')
    STATUS('This is a custom log level message')
    CRITICAL('This is a critical log level message')
    # FATAL('This is a critical message')

    # INFO('This is an informational message')
    # DEBUG('This is a debug message')
    # WARN('This is a warning message')
    # ERROR('This is an error message')
    # FATAL('This is a fatal message')
    # USER('This is a custom log level message')

    # EXCEPTION('This is an exception')
    # try:
    #    raise RuntimeError('Exception occured')
    # except RuntimeError as err:
    #    EXCEPTION('This is an exception message')
    #    pass


if __name__ == '__main__':
    main(argv[0])

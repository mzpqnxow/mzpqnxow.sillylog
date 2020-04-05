#!/usr/bin/env python3
import logging
from sillylog.log import get_logger, LOGLEVEL_TRACE

LOG, TRACE, DEBUG, INFO, WARN, ERROR, CRITICAL, EXCEPTION, STATUS = get_logger('main', log_level=LOGLEVEL_TRACE, datefmt='%h:%M:%s')


def test2(var):
    TRACE('helllapppapp!!!')


def test1():
    test2('ddd')


def main():
    DEBUG('test debug message')
    INFO('test info message')
    WARN('test warn message')
    ERROR('test error message')
    CRITICAL('test fatal message')
    STATUS('test status message')
    test1()

    # print(pretty_traceback())


if __name__ == '__main__':
    main()

import logging
from logging import CRITICAL, FATAL, ERROR, WARNING, DEBUG, INFO
from sys import argv
from os import rename, unlink
from os.path import basename, relpath
from lzma import open as lzma_open
from sys import stderr
import traceback

from sillylog.util import flex_mkdir

APPNAME = basename(argv[0])

LOGLEVEL_TRACE = DEBUG - 1
LOGLEVEL_USER = CRITICAL + 1

# logging.USER_LEVELV_NUM = CRITICAL + 1
# logging.addLevelName(logging.USER_LEVELV_NUM, "USER")


def pretty_traceback_lines(skip=0, width=24, indent='  '):
    traceback_lines = list()
    stackframe_list = traceback.extract_stack()
    stackframe_list.reverse()
    strackframe_list = stackframe_list[skip:]
    for frame_number, stack in enumerate(stackframe_list[skip:]):
        call_line = stack.line
        call_filename = stack.filename
        if call_filename.startswith('./'):
            call_filename = call_filename[2:]
        call_line_number = stack.lineno
        call_name = stack.name
        output_line = '{}#{:d} {}:{}:{}'.format(
            indent, frame_number, call_filename, call_name, call_line_number)
        traceback_lines.append('{} {}'.format(output_line.ljust(width), call_line))
    return traceback_lines


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


addLoggingLevel('USER', CRITICAL + 1)
addLoggingLevel('TRACE', DEBUG - 1)


class LevelBasedFormatter(logging.Formatter):
    def __init__(self, log_level_formats=None, fmt='%(levelname)s: %(msg)s', datefmt='%H:%M', style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self._initialize_level_formats(log_level_formats=log_level_formats)

    def _initialize_level_formats(self, log_level_formats=None):
        self._log_level_formats = dict()
        plain_fmt = '%(message)s'
        basic_fmt = '%(asctime)s(%(levelname)s) {} %(message)s '
        verbose_fmt = ('%(asctime)s(%(levelname)s)\t{} '
                       '%(name)8s %(filename)s::%(funcName)s '
                       '%(message)s')
        extra_verbose_fmt = ('%(asctime)s(%(levelname)s)\t{} '
                             '%(name)8s %(filename)s::%(funcName)s::%(lineno)d '
                             '%(message)s')
        extreme_verbose_fmt = ('%(asctime)s(%(levelname)s)\t{} '
                               '%(name)8s %(filename)s::%(funcName)s::%(lineno)d '
                               '%(message)s\n%(backtrace)s\n')
        # error_fmt = '\n... %(asctime)s %(levelname)-8s {} %(message)s\n'
        error_fmt = '\n...' + extra_verbose_fmt + '\n'
        self._log_level_formats[CRITICAL] = error_fmt
        self._log_level_formats[FATAL] = error_fmt
        self._log_level_formats[ERROR] = verbose_fmt
        self._log_level_formats[WARNING] = verbose_fmt
        self._log_level_formats[DEBUG] = extra_verbose_fmt
        self._log_level_formats[INFO] = basic_fmt
        self._log_level_formats[logging.USER] = plain_fmt

        self._log_level_formats[logging.TRACE] = extreme_verbose_fmt
        # Allow partial or full overrides, keep the defaults for any
        # levels that the caller doesn't provide
        if isinstance(log_level_formats, dict):
            self._log_level_formats.update(log_level_formats)

        # Stamp in the appname.. this could be made available using an adapter
        # but for now this is simpler
        for key in self._log_level_formats.keys():
            self._log_level_formats[key] = self._log_level_formats[key].format(APPNAME)

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt




        # Replace the original format with one customized by logging level
        if record.levelno not in self._log_level_formats.keys():
            raise RuntimeError('Incomplete logging implementation!')
        
        # Yeah, this is really, really bad... I'm sick of reading the logging
        # source to see how to properly do this ...
        # if record.levelno == logging.TRACE:
        #    lines = pretty_traceback_lines(skip=9)
        #    record.stack_info = '\n'.join(lines) + '\n'
        
        self._style._fmt = self._log_level_formats[record.levelno]
        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)
        # Restore the original format configured by the user
        self._style._fmt = format_orig
        return result


class LZMARotator:
    def __call__(self, source, dest):
        rename(source, dest)
        with open(dest, 'rb') as log_fd, lzma_open('%s.gz'.format(dest), 'wb') as lzma_fd:
            lzma_fd.writelines(log_fd)
        unlink(dest)


def get_logger(
    name=None,
    log_level=logging.DEBUG,
    file_log_level=None,
    datefmt='%H:%M',
    logfile_path=None,
    auto_mkdir=False,
    shell_expand=True,
    compress=True
):
    formatter = LevelBasedFormatter()
    console_handler = logging.StreamHandler(stream=stderr)
    console_handler.setFormatter(formatter)
    logging.root.addHandler(console_handler)
    logging.root.setLevel(log_level)

    logger = logging.getLogger(name if name else APPNAME)

    if logfile_path:
        if file_log_level is None:
            file_log_level = log_level
        if auto_mkdir is True:
            logfile_path = flex_mkdir(logfile_path, shell_expand=shell_expand, is_filename=True)
        file_handler = logging.handlers.TimedRotatingFileHandler(logfile_path, when='d', interval=1, backupCount=7)
        file_handler = file_log_level
        if compress is True:
            file_handler.rotator = LZMARotator
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    class BacktraceFilter(logging.Filter):
        """Dynamically add a backtrace into the logging record

        This allows %(backtrace)s to be accessed from a log format string

        I'm not thrilled with the magic number here, but it seems to
        be fixed, at least for now. It's not pretty though and we are
        at the mercy of Python3 internals here. If things change .. ugh

        To do this more correctly, I guess `pretty_trackback_lines` should
        iterate over the stack frames and based on some rule, determine when
        the boilerplate stack frames end. There must be a simple way to do
        this but it escapes me now and I don't want to deal with it anymore

        BTW- since when is logging.Filter.filter() a staticmethod? Weird...

        -AG

        """
        @staticmethod
        def filter(record):
            record.backtrace = '\n'.join(pretty_traceback_lines(skip=6))
            return True

    logger.addFilter(BacktraceFilter)

    return (
        logger,
        logger.trace,
        logger.debug,
        logger.info,
        logger.warning,
        logger.error,
        logger.critical,
        logger.exception,
        logger.user)
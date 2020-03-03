"""Reusable logging package with some nice features

Note that the recommended usage examples violate specific PEP8 and other commonly accepted
Python naming conventions. The examples suggest you name the logger objects using all caps.
This is obviously not required, it is simply this way because I am a C programmer and have
a preference for all-capital logging functions, having always used all-caps C preprocessor
macros for debugging. If you want to be more compliant, just ignore the usage example and
rename `LOG`, `DEBUG`, `INFO`, etc. to their lowercase versions when calling `get_logger`

=== Usage ===
The idea is that the top of each file, you have the following boilerplate call:

--- snip ---
LOG, DEBUG, INFO, USER, WARN, ERROR, FATAL, EXCEPTION = get_logger(__name__, None, level=logging.INFO, new=True)
--- snip ---

The DEBUG, INFO, USER, etc. imports are all functions that log, same as logging.debug, etc. They
are not logger class instances. Call them directly, e.g. `DEBUG('Some debug message')` as opposed
to `DEBUG.log('Some debug message')`

Raw log output will use the basename of the asbsolate realpath to the python program/file that
was **invoked at start time**. It will also of course have the module name and the second argument
can be used as an identifier when it is a library. It is also quite normal to leave the second argument
as None

Once this command is executed, logs will go to the screen as well as to a rotating logfile

**NOTE**: The Handler was overwritten so that a call to `FATAL()` actually causes the process to exit
          do don't call `FATAL()` unless you really mean it!

=== General Notes / Caveats ===

The code here is a bit sloppy, though the style is mostly compliant with PEP8. There is functionality
present that is not actually used and could be removed. For now it is left in or commented out

I am not nearly an expert in Python logging idioms, so there are almost certainly some 'not quite right'
usages of the logging functionality here. Please submit a PR if you use this and identify such things,
or at least create an Issue

=== TODO(AG) ===
 * Utilize the Python logging configuration file support

"""
# Python Standard Libraries
import inspect
import logging
from logging import (
    Formatter,
    Logger,
    StreamHandler,
    addLevelName,
    getLoggerClass,
    setLoggerClass
)
from logging.handlers import (
    DatagramHandler,
    HTTPHandler,
    MemoryHandler,
    RotatingFileHandler,
    SocketHandler,
    SysLogHandler,
    TimedRotatingFileHandler,
    WatchedFileHandler
)
from os import mkdir
from os.path import (
    basename,
    expanduser,
    isdir,
    join as join_path,
    sep as DIRSEP
)
from sys import argv as ARGV

# TODO: Make a simple .ini path in the package for this ... anything other than this
#       Can't use .capamrc due to circular dependencies most likely, so I'm not
#       going to try ...

APPNAME = basename(ARGV[0])

# Add new log-level for user-friendly (readable) console I/O
# Always prints regardless of log level and is just a simple
# message. Meant to replace a simple `print()`
LOGLEVEL_STATUS = logging.CRITICAL + 10


class PipelineLogger(Logger):
    """Helper when adding a custom log level

    There are probably other ways to do this, and they may be more
    correct, but this doesn't require much code so it seems good to me
    """
    def user(self, msg, *args, **kwargs):
        """Stub for the custom method"""
        if self.isEnabledFor(LOGLEVEL_STATUS):
            self._log(LOGLEVEL_STATUS, msg, args, **kwargs)


class ExitingStreamHandler(StreamHandler):
    """This handler behaves as normal but exits the process when invoked as 'FATAL'

    This seemed nice but it is actually kind of a dumb idea ... the exit
    from a FATAL error should be handled in the application, not the logging
    framework

    Use CRIT to log messages if you don't want to exit here. CRIT and FATAL are
    the same log level
    """
    def __init__(self):
        super().__init__()

    def emit(self, record):
        # super(ExitingStreamHandler, self).emit(record)
        super().emit(record)
        if record.levelname == 'FATAL':
            # levelno is the same for CRIT and FATAL so levelname is checked
            # func, lineno = _function_lineno(depth=7)
            exit(1)
        if record.exc_info:
            raise RuntimeError('Unsupported condition, BUG/TODO!')


class LevelBasedFormatter(logging.Formatter):
    """Python logging Formatter that supports different messages for different levels

    Example:
        ```
        $ ./test.py
        This is an informational message
        2020-02-24@16:34.57 DEBUG     test.py ./test.py test.py::main::64 This is a debug message
        2020-02-24@16:34.57 WARNING   This is a warning message
        2020-02-24@16:34.57 ERROR     This is an error message
        2020-02-24@16:34.57 This is a custom log level message

        ... 2020-02-24@16:34.57 CRITICAL , This is a critical log level message
        ```

    """
    def __init__(self, *args, **kwargs):
        fmt = kwargs.get('fmt', None)
        datefmt = kwargs.get('datefmt', None)
        super().__init__(fmt=fmt, datefmt=datefmt, style='%')
        self._fmt_save = self._style._fmt

    def usesTime(self):
        """Bug somewhere, need to fake this or asctime key won't be present"""
        return '%(asctime)' in self._style._fmt

    def formatMessage(self, record):
        """Custom formatMessage to use a different format for each log level

        This function normall only does:

        return self._style.format(record)

        TODO: Dynamic configuration, not hard, just don't need it right now

        """
        self._fmt_save = self._style._fmt

        if record.levelno in (logging.ERROR, logging.WARNING):
            self._fmt = self._style._fmt = '%(asctime)s %(levelname)-9s %(message)s'  # Stand out with prefix/suffix newlines
        elif record.levelno in (LOGLEVEL_STATUS, ):
            self._fmt = self._style._fmt = '%(asctime)s %(message)s'
        elif record.levelno in (logging.CRITICAL, logging.FATAL):
            # CRIT and FATAL are actually the same levelno, just different levelname
            self._fmt = self._style._fmt = '\n... %(asctime)s %(levelname)-9s, %(message)s\n'
        elif record.levelno in (logging.DEBUG, ):
            fmt = '%(asctime)s'
            fmt += ' %(levelname)-9s '
            fmt += APPNAME
            fmt += ' %(name)8s'
            fmt += ' %(filename)s::%(funcName)s::%(lineno)d'
            fmt += ' %(message)s'
            self._fmt = self._style._fmt = fmt
        elif record.levelno in (logging.INFO, ):
            fmt = '%(asctime)s'
            fmt += ' %(levelname)-9s '
            fmt += ' %(name)8s'
            fmt += ' %(message)s'

        # Hack for asctime ...
        if '%(asctime)' in self._style._fmt:
            record.asctime = self.formatTime(record, self.datefmt)

        msg = self._style.format(record)
        self._fmt = self._style._fmt = self._fmt_save

        return msg

    def emit(self, record):
        """This is not necessary, kill it after some testing"""
        raise RuntimeError('Unexpected condition, BUG/TODO!')
        super().emit(record)


def _apply_log_handler(logger, log_format, log_level, h_class, *args, **kwargs):
    """Private function for getting a handler, basic flexible wrapper for any class"""
    log_handler = h_class()
    log_handler.setLevel(log_level)
    custom_formatter = LevelBasedFormatter(fmt=log_format, datefmt='%Y-%m-%d@%H:%M.%S', style='%s')
    log_handler.setFormatter(custom_formatter)
    logger.addHandler(log_handler)
    return log_handler


def _mkdir_parents(dirname):
    """emulate mkdir -p behavior"""
    path_stack = ''
    for element in dirname.split(DIRSEP):
        if not isdir(dirname):
            if not element:
                continue
            path_stack = join_path(DIRSEP, path_stack, element)
            if not isdir(path_stack):
                mkdir(path_stack)


def _function_lineno(depth=7):
    """Print frame information, meant to be called from a logging function

    In Python3, you will need to go 7 frames deep to find the actual caller
    frame. Pretty ugly magic number, and can change with
    """
    caller_frame = inspect.stack()[depth]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    return info.function, info.lineno


def get_logger(
        name,
        source_name,
        logpath=None,
        rotate_params=(0x4000000, 7),
        mklogdir=True,
        fmt='%(message)s',
        datefmt='%Y-%m-%d@%H:%M.%S',
        file_log_level=None,
        console_log_level=None,
        level=None,
        new=False):
    """Purpose built function for setting up loggers or usin in a specific app

    TODO: Work out where to store logs !!

    Note:
        This function will log several different ways, but will only present one logger
          1. Daily logs for each severity will be written and turned over at midnight
          2. A size-based log file will be written for all log data that will be turned
             at a specific size.
          3. A console (stdout/stderr) log handler will also be present for interactive
             use of an application

        All rotated logs will be compressed with bz2 to save size. This is native supported
        in Pyhthon 2.7 because it uses codecs.open, which supports 'bz2' as an encoding.

        Currently, you have no option to disable bz2, sorry.

    Args:
        name (str): The name of the calling module (should be passed from the caller as __name__)
        source_name (str): The name of source, like the package name, optionally None.
        logpath (str): Absolute path where the logger will place logs. It is suggested that you place this
                       within your applications root or the virtual environment root. You can find
                       the absolute path to a venv/log directory. You can identify your absolute
                       root path using dirname(realpath(__file__)) in your entry point, and then
                       making use of os.path.join() from there to get to a log directory

        rotate_params tuple(int, int): The maximum size for size rotated files and how many
                                       rotated files to keep. Default 64MB, 7 files
        mklogdir (bool): Create the entire path up to logpath if it doesn't exist. This is not
                         enabled by default because you should have already created it, placed
                         a placeholder (i.e. .keep) in it, and checked it in to your repository.
                         Make sure you .gitignore logfiles as well.
        fmt (str): Python logging module log format string. Optional


    Returns:
        logging.Logger: The return value. A configured Python logging.Logger

    Raises:
        RuntimeError: if a slash character is in `source_name`
        RuntimeError: if `logpath` is not an absolute path

    """

    # These are the two steps to add a log level, at a high level
    setLoggerClass(PipelineLogger)

    if logpath is None:
        logpath = expanduser('~/log')

    if file_log_level is None:
        file_log_level = level

    if console_log_level is None:
        console_log_level = level

    if level is None:
        level = logging.DEBUG

    if fmt is None:
        fmt = '%(asctime)s'
        fmt += ' %(levelname)5s '
        fmt += APPNAME
        fmt += ' %(name)8s'
        fmt += ' %(filename)s::%(funcName)s::%(lineno)d'
        fmt += ' %(message)s'

    if source_name is None:
        source_name = ''
    elif '/' in source_name:
        raise RuntimeError('source_name can not contain a slash character, makes no sense ...')

    if logpath[0] != '/':
        raise RuntimeError('logpath must be an absolute path, sorry')

    if mklogdir is True:
        _mkdir_parents(logpath)

    # TODO: Should this be set this way, without a handler?
    #       Should it be NOTSET?
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.propagate = False

    # You can mess around with different handlers if you'd like
    # but I don't use them

    # filename = join_path(logpath, '{}.log'.format(APPNAME))
    # _apply_log_handler(
    #     logger,
    #     log_format,
    #     file_log_level,
    #     TimedRotatingFileHandler,
    #     filename,
    #     when='midnight',
    #     interval=1)
    # # rotating_file_handler.suffix = '%Y%m%d'

    # _apply_log_handler(
    #     logger,
    #     log_format,
    #     file_log_level,
    #     RotatingFileHandler,
    #     join_path(logpath, '{}.log'.format(APPNAME)),
    #     maxBytes=rotate_params[0],
    #     backupCount=rotate_params[1])

    # Basic console stderr/stdout handler
    log_handler = _apply_log_handler(
        logger,
        fmt,
        console_log_level,
        ExitingStreamHandler)

    log_handler.setFormatter(LevelBasedFormatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(log_handler)
    logger.setLevel(level)

    # if new is False:
    #     raise NotImplemented('Not implemented / tested!')
    #     return logger, logger.debug, logger.info, logger.warning, logging.error, logging.critical, logging.exception

    return logger, logger.debug, logger.info, logger.warning, logger.error, logger.critical, logger.exception
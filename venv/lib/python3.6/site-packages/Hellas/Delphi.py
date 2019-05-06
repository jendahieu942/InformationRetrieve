"""This module contains classes and functions useful for pretty/color printing to console or logs
it is named after `Delphi <http://en.wikipedia.org/wiki/Delphi>`_ the famous city where
ancient `Oracle of Delphi <https://en.wikipedia.org/wiki/Pythia>`_ was located.
"""


import sys
import logging
from logging import handlers  # in python 3 not in logging.handlers
import time
from Hellas.Sparta import DotDot, seconds_to_DHMS, class_name_str
from Hellas import _IS_PY2
try:
    import simplejson as anyjson
except ImportError as e:
    import json as anyjson

auto_retry_msg_frmt = "auto-retry: class: {} e: {} tries:({:d} of {:d}), waitSecs: {:.2f}\n\tfunc: {}\n\targs:[{}]\n\tkwargs:[{}] msg:{}"

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())  # Prevents No handlers found warning


class Color(object):
    """some basic color handling for printing in color

    .. Warning:: This class will **NOT** work in windows OS unless complemented by
        library `colorama <https://pypi.python.org/pypi/colorama>`_

    :Example:
        >>> cl = Color()
        >>> cl.printc("this is red", "red")
    """
    colors = DotDot({
        'black':    (0, 30),    'gray_br':   (0, 37),
        'blue':     (0, 34),    'white':     (1, 37),
        'green':    (0, 32),    'blue_br':   (1, 34),
        'cyan':     (0, 36),    'green_br':  (1, 32),
        'red':      (0, 31),    'cyan_br':   (1, 36),
        'purple':   (0, 35),    'red_br':    (1, 31),
        'yellow':   (0, 33),    'purple_br': (1, 35),
        'gray_dk':  (1, 30),    'yellow_br': (1, 33),
        'normal':   (0,)
        })

    @classmethod
    def help(cls):
        """prints named colors"""
        print("for named colors use :")
        for c in sorted(list(cls.colors.items())):
            print("{:10} {}".format(*c))

    @classmethod
    def color_code(cls, color):
        """ returns code for color
         :param tuple_or_code color: either a tuple as in colors.values or a string key to colors dictionary
        """
        if not isinstance(color, tuple):
            color = cls.colors[color]
        return "{:d};{}".format(color[0], str(color[1]) if len(color) == 2 else "")

    @classmethod
    def color_switch_txt(cls, color=colors.red):
        return "\033[{}m".format(cls.color_code(color))

    @classmethod
    def color_txt(cls, txt="", color=None):
        if _IS_PY2 and isinstance(txt, unicode):
            txt = txt.encode("utf-8")
        return "{}{}\033[0m".format(cls.color_switch_txt(color), txt)

    @classmethod
    def printc(cls, txt, color=colors.red):
        """Print in color."""
        print(cls.color_txt(txt, color))

    @classmethod
    def color_switch_print(cls, color):
        print(cls.color_switch_txt(color))


class ColoredFormatter(logging.Formatter):
    """a logging formatter for printing in color works only in linux
    on an non linux system it returns plain text
    """
    if sys.platform.startswith('linux'):
        color = Color()
        clr_name = color.colors

        def format(self, record):
            levelno = record.levelno
            if(levelno >= 50):
                clr = self.clr_name.red_br       # CRITICAL / FATAL
            elif(levelno >= 40):
                clr = self.clr_name.red          # ERROR
            elif(levelno >= 30):
                clr = self.clr_name.yellow       # WARNING
            elif(levelno >= 20):
                clr = self.clr_name.green        # INFO
            elif(levelno >= 10):
                clr = self.clr_name.purple_br    # DEBUG
            else:
                clr = self.cls_name.normal       # NOTSET etc
            return self.color.color_txt(logging.Formatter.format(self, record), clr)
    else:
        def format(self, record):
            return logging.Formatter.format(self, record)


def logging_format(verbose=2, style='txt'):
    """returns a format
    :parameter:
        - str style: defines style of output format (defaults to txt)
            - txt plain text
            - dict like text which can be casted to dict
    """
    frmt = "'dt':'%(asctime)s', 'lv':'%(levelname)-7s', 'ln':'%(name)s'"

    if verbose > 1:
        frmt += ",\t'Func': '%(funcName)-12s','line':%(lineno)5d, 'module':'%(module)s'"
    if verbose > 2:
        frmt += ",\n\t'file':'%(filename)s',\t'Process':['%(processName)s', %(process)d], \
                'thread':['%(threadName)s', %(thread)d], 'ms':%(relativeCreated)d"
    frmt += ",\n\t'msg':'%(message)s'"
    if style == "dict":
        frmt = "{" + frmt + "}"
        frmt = frmt.replace(" ", "").replace("\n", "").replace("\t", "")
    if style == "txt":
        frmt = frmt.replace("'", "").replace(",", "")
    return frmt


class LoggingColorHandler(logging.StreamHandler):
    def __init__(self, level=logging.NOTSET, verbose=2):
        super(LoggingColorHandler, self).__init__()
        self.setLevel(level)
        formatterC = ColoredFormatter(logging_format(verbose, 'str'))
        formatterC.converter = time.gmtime
        self.setFormatter(formatterC)


def logger_multi(
        loggerName="",  # top
        level_consol=logging.DEBUG,
        level_file=logging.DEBUG,
        filename=None,
        verbose=1,
        when='midnight',
        interval=1,
        backupCount=7):
    """a logger that logs to file as well as as screen
    see http://pythonhosted.org//logutils/ http://plumberjack.blogspot.gr/2010/10/supporting-alternative-formatting.html

    :Todo:
      - use new style formating for python > v3 i.e formatter = logging.Formatter(frmt.replace(" ", ""), style='{')
        #frmtC = frmt.translate(dict((ord(c), '') for c in "'{},"))

    :Parameters: `see <https://docs.python.org/2/library/logging.html#module-logging>`_
    :Example:
        >>> LOG = logger_double('', level_consol=logging.DEBUG, level_file=logging.DEBUG, verbose=3, filename="~\f.log")
    """
    logger = logging.getLogger(loggerName)
    logger.setLevel(min(level_consol if level_consol else 100, level_file if level_file else 100))
    # logger.disable_existing_loggers = False
    if level_file:
        if filename is None:
            filename = "~\py.log"
        formatter = logging.Formatter(logging_format(verbose, 'str'))
        formatter.converter = time.gmtime
        hf = handlers.TimedRotatingFileHandler(
            filename, when=when, interval=interval,
            backupCount=backupCount, encoding='utf-8', delay=False, utc=True)
        hf.setFormatter(formatter)
        hf.setLevel(level_file)
        logger.addHandler(hf)
    if level_consol:
        logger.addHandler(LoggingColorHandler(level=level_consol, verbose=verbose))
    return logger


def auto_retry(exception_t, retries=3, sleepSeconds=1, back_of_factor=1, msg='', auto_log=1, raise_on_failure=True):
    """a generic auto-retry function  @wrapper - decorator

    :param Exception exception_t: exception (or tuple of exceptions) to auto retry
    :param int retries: max retries before it raises the Exception (defaults to 3)
    :param int_or_float sleepSeconds: base sleep seconds between retries (defaults to 1)
    :param int back_of_factor: factor to back off on each retry (defaults to 1)
    :param str msg: message to append to logs
    :param int auto_log: (0 | 1 | 2) logs (exception) failures if > 0 logs (info) retries also if > 1
    :param bool raise_on_failure: if True will re-raise exception when retries are exhausted (defaults to True)
    :returns:
        function result if successful (on first place or after retrying)
        the *last* retry Exception if not successful, check not isinstance(result , Exception) to see if it managed to succeed
    """
    def wrapper(func):
        def fun_call(*args, **kwargs):
            tries = 0
            while tries < retries:
                try:
                    return func(*args, **kwargs)
                except exception_t as e:
                    tries += 1
                    sleep_seconds = sleepSeconds * tries * back_of_factor
                    if auto_log > 0:
                        ermsg = auto_retry_msg_frmt.format(class_name_str(e, True), e, tries, retries, sleep_seconds, func.__name__, args, kwargs, msg)
                    if tries < retries:
                        if auto_log > 1:
                            LOG.info(ermsg)
                        time.sleep(sleep_seconds)
                    else:
                        if auto_log > 0:
                            LOG.exception(ermsg)
                        if raise_on_failure:
                            raise
                        return e
        return fun_call
    return wrapper


@auto_retry((ZeroDivisionError),  msg='auto_retry_test', raise_on_failure=True)
def auto_retry_test():
    return 1 / 0


def pp_obj(obj, out_path=None, indent=4, sort_keys=False, ensure_ascii=False, default=None):
    """
    pretty prints a (list tuple,  dict etc) object

    :useful:
        - when we want to avoid importing pprint if we have already imported json
        - when we want to pprint to file without breaking json compatibility
    """
    rt = anyjson.dumps(obj, sort_keys=sort_keys, indent=indent, ensure_ascii=ensure_ascii,
                       separators=(',', ': '), default=default, namedtuple_as_object=False)
    # unicode_available
    if out_path is None:
        return rt
    else:
        with open(out_path, 'w') as out:
            out.write(rt)


def time_func(func):
    """
    time a function decorator
    :param args: any args to pass to the function
    :paran kwargs: any key arguments to pass to the function
        (if 'operations' is in kwargs keys it is used to calculate operations per second)

    """
    def timed(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        secs = time.time() - ts
        ops_ps = kwargs.get('operations', secs) / secs
        print ("finc{} took: {} {:2.4f} operations/sec={:5.2f}".format(func.__name__, seconds_to_DHMS(secs), secs, ops_ps))
        return result
    return timed


@time_func
def time_func_example(seconds=10, **kwargs):
    """time a functiondecorator example"""
    for i in range(1, seconds + 1):
        time.sleep(1)
    return i


def visualise(seq, sort=lambda x: x[0]):
    """visualises as seq or dictionary"""
    frmt = "{:6} {:8,d} {}"
    if isinstance(seq, dict):
        seq = seq.items()
    if sort:
        seq = sorted(seq, key=sort)
    mx, mn = max([i[1] for i in seq]), min([i[1] for i in seq])  
    range = mx - mn
    for i in seq:
        v = int((i[1] * 100) / range)
        print (frmt.format(i[0], i[1], "*" * v))


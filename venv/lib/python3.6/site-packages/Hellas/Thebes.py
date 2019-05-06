# -*- coding: utf-8 -*-
"""yet some more code snippets named after the ancient city of `Thebes <https://en.wikipedia.org/wiki/Thebes,_Greece>`_
"""

import re
from Hellas.Sparta import chunks_str, seconds_to_DHMS
from Hellas.Sparta import DotDot, FMT_DT_GENERIC
from datetime import datetime


def format_header(frmt, return_len=False):
    """creates a header string from a new style format string useful when printing dictionaries

    :param str frmt: a new style format string
    :returns: a table header string

    assumptions for frmt specs:
        - all have a separator = '|' and include a key size format directive i.e.: '{key:size}'
        - no other character allowed in frmt except separator

    :Example:
        >>> frmt = '|{count:12,d}|{percent:7.2f}|{depth:5d}|'
        >>> data_dict = {'count': 100, 'percent': 10.5, 'depth': 10}
        >>> print(format_header(frmt)); print(frmt.format(**data_dict))
        ............................
        |   count    |percent|depth|
        ............................
        |         100|  10.50|   10|

    """
    names = re.sub("{(.*?):.*?}", r"\1", frmt)
    names = [i for i in names.split("|") if i]
    frmt_clean = re.sub("\.\df", r"", frmt)                 # get read of floats i.e {:8.2f}
    sizes = re.findall(r':(\d+)', frmt_clean)
    frmt_header = "|{{:^{}}}" * len(sizes) + "|"
    header_frmt = frmt_header.format(*sizes)
    header = header_frmt.format(*names)
    header_len = len(header)
    header = "{}\n{}\n{}\n".format("." * header_len, header, "." * header_len)
    return header.strip() if return_len is False else (header.strip(), header_len)


def chunks_str_frame(a_str, n=None, center=True):
    """places a frame around a string
    :Parameters:
        - a_str: string to frame
        - n: number of chars in each line
        - center: center string in frame if True and n > len(str)

    :Example:
        >>> print(chunks_str_frame('the quick brown fox', 44))
        ╔════════════════════════════════════════════╗
        ║            the quick brown fox             ║
        ╚════════════════════════════════════════════╝
        >>> print(chunks_str_frame('the quick brown fox',12, False))
        ╔════════════╗
        ║the quick br║
        ║own fox     ║
        ╚════════════╝
    """
    if n is None:
        n = len(a_str)
    elif n > len(a_str) and center is True:
        a_str = a_str.center(n)
    spcs = "" if n == 1 or n == len(a_str) else " " * (n - (len(a_str) % n))
    n = len(a_str) if n is None else n
    r = chunks_str(a_str, n, "║\n║")
    return "╔{}╗\n║{}{}║\n╚{}╝".format('═' * n, r, spcs, '═' * n)


class MacAddress(object):
    """ stores mac as int
    """
    _mac_regx = re.compile(r'^([0-9A-F]{1,2})' + '\:([0-9A-F]{1,2})'*5 + '$', re.IGNORECASE)
    # @todo move class to Hellas

    def __init__(self, mac_str, validate=True):
        if validate is False or self.mac_validate(mac_str) is not None:
            self._mac = self.mac_to_int(mac_str)
        else:
            raise ValueError

    def __int__(self):
        return self._mac

    def __str__(self):
        return self.mac_expand(self.mac_from_int(self._mac), upper=False, lower=False)

    @classmethod
    def mac_validate(cls, mac_str):
        return cls._mac_regx.match(mac_str)

    @classmethod
    def mac_compress(cls, mac, upper=True, lower=False):
        mac = mac.replace(":", "")
        return mac.upper() if upper else mac.lower() if lower else mac

    @classmethod
    def mac_expand(cls, mac, upper=True, lower=False):
        """expands a compressed mac addres str ie (AC8674075628) to mac address (AC:86:74:07:56:28) also makes it lower/upper case"""
        mac = ":".join(["".join(i) for i in zip(mac[::2], mac[1::2])])
        return mac.upper() if upper else mac.lower() if lower else mac

    @classmethod
    def mac_to_int(cls, mac):
        return int(cls.mac_compress(mac, upper=False, lower=False), 16)

    @classmethod
    def mac_from_int(cls, mac_int):
        """returns a mac string from int  'c81ee716c167'
           to make it proper mac string pass result to mac_expand
        """
        return hex(mac_int)[2:]


class Progress(object):
    def __init__(self, max_count=None, head_line="progress", extra_frmt='', extra_dict={}, every_seconds=None, every_mod=None):
        self._frmt = '|{cnt:10,d}|{date_time:15}|{operations:16,d}|{per_sec:12,d}|{run_time:12}|'
        if max_count is not None:
            self._frmt += '{ETA:12}|{percent:8.2f}|'
        self._frmt += extra_frmt
        self.max_count = max_count
        self.extra_frmt = extra_frmt
        self.head_line = head_line
        self.header, self.header_len = format_header(self._frmt, True)
        if every_seconds is None and every_mod is None:
            every_seconds = 60
        self.every_seconds = every_seconds
        self.every_mod = every_mod
        self._dict = DotDot()
        self.reset(extra_dict)
        self.print_header()
        self.dt_start = datetime.now()
        self.state = 0  # 0  no print yet, 1 some print occured, 2 have been on print_end

    def progress(self, inc=1, extra_dict=None):
        self._dict.operations += inc
        if self.every_mod is not None:
            if self._dict.operations % self.every_mod == 0:
                self.print_stats(extra_dict)
                return
        elif (datetime.now() - self.dt_last_print).total_seconds() > self.every_seconds:
            self.print_stats(extra_dict)
            return
        elif self.max_count is not None and self._dict.operations == self.max_count:
            self.print_stats(extra_dict)
            self.print_end(extra_dict)
            return
        elif self.state == 0:
            self.state = 1
            self.print_stats(extra_dict)

    def print_stats(self, extra_dict):
        self.dt_last_print = datetime.now()
        self._dict.cnt += 1
        self._dict.date_time = self.dt_last_print.strftime(FMT_DT_GENERIC)
        if extra_dict is not None:
            self._dict.update(extra_dict)
        elapsed = (self.dt_last_print - self.dt_start).total_seconds()
        self._dict.run_time = seconds_to_DHMS(elapsed)
        if self.max_count:                          # we don't check just for None to avoid div by 0 if max_count is 0
            perc = (self._dict.operations / float(self.max_count))
            self._dict.percent = 100 * perc
            self._dict.per_sec = 0 if self._dict.operations < 10 else int(self._dict.operations / (self.dt_last_print - self.dt_start).total_seconds())
            self._dict.ETA = seconds_to_DHMS((elapsed * (1 / (perc if perc > 0 else 1))) - elapsed)
        print(self._frmt.format(**self._dict))
        if self._dict.operations == self.max_count:
                self.print_end()

    def reset(self, extra_dict={}):
        self._dict = DotDot({'cnt': 0, 'date_time': datetime.now().strftime(FMT_DT_GENERIC),
                             'operations': 0, 'per_sec': 0, 'percent': 0.0, 'run_time': '', 'ETA': ''})
        self._dict.update(extra_dict)
        self.dt_last_print = datetime.now()

    def print_header(self):
        if self.head_line:
            print(chunks_str_frame(self.head_line, self.header_len - 2, center=True))
        print(self.header)

    def print_end(self, extra_dict=None, override_ended=False):
        if (not self.state == 2) or override_ended:
            self.state = 2
            print('.' * self.header_len)
            self.print_stats(extra_dict)
            print('.' * self.header_len)


    @classmethod
    def test(cls, every_seconds=2, every_mod=None):
        extra_ftmt, extra_dict = "{foo:4d}|", {'foo': 4} 
        prg = Progress(max_count=100000000, head_line="test progress", extra_frmt=extra_ftmt, extra_dict=extra_dict, every_seconds=every_seconds, every_mod=every_mod)
        for cnt in range(0, 100000000):
            if cnt % 1000 == 0:
                prg.progress(1000, extra_dict=extra_dict)


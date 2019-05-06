"""mostly dict list and file related functions and classes named after
the ancient city of `Pella <https://en.wikipedia.org/wiki/Pella>`_
"""

from copy import copy
import signal
import os
from base64 import b64encode
from random import random
from Hellas.Sparta import Error


class ErrorFileTooBig(Error):
    pass


# file operations -------------------------------------------------------------
def read_file(path, mode='rb'):
    """
    :param path: fool pathname string for a file to read
    :param mode: file open mode defaults to 'rb'
    """
    with open(path, 'rb') as fin:
        return fin.read()


def file_to_base64(path_or_obj, max_mb=None):
    """converts contents of a file to base64 encoding

    :param str_or_object path_or_obj: fool pathname string for a file or a file like object that supports read
    :param int max_mb: maximum number in MegaBytes to accept
    :param float lon2: longitude of second place (decimal degrees)

    :raises ErrorFileTooBig: if file contents > max_mb (see :class:`ErrorFileTooBig`)
    :raises IOError: if file path can't be found (Also possible other exceptions depending on file_object)
    """
    if not hasattr(path_or_obj, 'read'):
        rt = read_file(path_or_obj)
    else:
        rt = path_or_obj.read()
    if max_mb:
        len_mb = len(rt) / (10024.0 * 1000)
        if len_mb > max_mb:
            raise ErrorFileTooBig("File is too big ({.2f} MBytes)" (len_mb))
    return b64encode(rt)


# dictionary operations -------------------------------------------------------
def dict_copy(a_dict, exclude_keys_lst=[], exclude_values_lst=[]):
    """a **SALLOW** copy of a dict that excludes items in exclude_keys_lst and exclude_values_lst
    useful for copying locals() etc..

    :param dict a_dict: dictionary to be copied
    :param list exclude_keys_lst: a list or tuple of keys to exclude
    :param list exclude_values_lst: a list or tuple of values to exclude

    .. Warning:: remember it is NOT a deep copy
    """
    return dict([copy(i) for i in list(a_dict.items())
                 if i[0] not in exclude_keys_lst and i[1] not in exclude_values_lst])


def dict_clip(a_dict, inlude_keys_lst=[]):
    """returns a new dict with keys not in included in inlude_keys_lst clipped off"""
    return dict([[i[0], i[1]] for i in list(a_dict.items()) if i[0] in inlude_keys_lst])


# list operations -------------------------------------------------------------
def list_randomize(lst):
    """returns list in random order"""
    return sorted(lst, key=lambda x: random())


def list_pp(ll, separator='|', header_line=True, autonumber=True):
    """pretty print list of lists ll"""
    if autonumber:
        for cnt, i in enumerate(ll):
            i.insert(0, cnt if cnt > 0 or not header_line else '#')

    def lenlst(l):
        return [len(str(i)) for i in l]

    lst_len = [lenlst(i) for i in ll]
    lst_rot = zip(*lst_len[::-1])
    lst_len = [max(i) for i in lst_rot]
    frmt = separator + separator.join(["{!s:"+str(i)+"}" for i in lst_len]) + separator
    if header_line:
        header_line = '-' * len(frmt.format(*ll[0]))
    for cnt, l in enumerate(ll):
        if cnt < 2 and header_line:
            print(header_line)
        print(frmt.format(*l))
    if header_line:
        print(header_line)
    return lst_len


# signal -----------------------------------------------------------------------
def signal_terminate(on_terminate):
    """a common case program termination signal"""
    for i in [signal.SIGINT, signal.SIGQUIT, signal.SIGUSR1, signal.SIGUSR2, signal.SIGTERM]:
        signal.signal(i, on_terminate)


# classes -----------------------------------------------------------------------
class Base62(object):
    """unsigned integer coder class codes to and from base 62, useful for compressing integer values

    .. Warning:: any encoded values can only be decoded by this class

    :Example:
        >>> b62 = Base62()
        >>> vl = 2 ** 24
        16777216
        >>> b62.encode(vl)
        '18OWG'
        >>> b62.decode('18OWG')
        16777216
    """
    symbols = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    numeric_symbols = symbols[:10]

    def __repr__(self):
        return "<base62: (%s)>" % (self.symbols)

    @staticmethod
    def _code(number, from_digits, to_digits):
        x = 0
        len_from_digits = len(from_digits)
        len_to_digits = len(to_digits)
        for ch in str(number):
            x = x * len_from_digits + from_digits.index(ch)
        if x == 0:
            res = to_digits[0]
        else:
            res = ''
            while x > 0:
                digit = x % len_to_digits
                res = to_digits[digit] + res
                x = int(x // len_to_digits)
        return res

    @classmethod
    def encode(cls, number):
        return cls._code(number, cls.numeric_symbols, cls.symbols)

    @classmethod
    def decode(cls, number):
        return int(cls._code(number, cls.symbols, cls.numeric_symbols))


def obj_id_expanded(obj=None, size=99):
    """
    :param obj (objectj): optional
    :param size (int): optional size of id(obj) to include defaults to 99

    :Returns: id: (str) an id that of the form machine-name|ppid|pid|id(obj)
    """
    return "{}|{}|{}{}".format(os.uname()[1], os.getppid(), os.getpid(), "" if obj is None else "|" + str(id(obj))[-size:])

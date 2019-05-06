"""This module contains some pickle and compress code snippets named after the city of
`Olympia <https://en.wikipedia.org/wiki/Olympia,_Greece>`_ where first Olympic games were held
"""

import zlib
import pickle


def pickle_compress(obj, print_compression_info=False):
    """pickle and compress an object"""
    p = pickle.dumps(obj)
    c = zlib.compress(p)
    if print_compression_info:
        print ("len = {:,d} compr={:,d} ratio:{:.6f}".format(len(p), len(c), float(len(c))/len(p)))
    return c


def pickle_decompress(obj):
    """ decompress  a pickle_compress object"""
    return pickle.loads(zlib.decompress(obj))


def pickle_compress_test(obj, print_compression_ratio=True):
    """verifies id an object is pickable and can be compressed"""
    cm = pickle_compress(obj, print_compression_ratio)
    dc = pickle_decompress(cm)
    return True if dc == obj else False


def pickle_compress_str(obj, print_compression_info=False):
    """ str gets better compression ration """
    return pickle_compress(str(obj), print_compression_info)


def pickle_decompress_str(obj):
    """ decompress pickle_compressed as str

    .. Warning:: it uses 'eval' use it carefully
    """
    return eval(pickle_decompress_str(obj))
